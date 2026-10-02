from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from apps.common.permissions import IsCustomerUser, IsOwnerOfOrder
from apps.orders.models import Order, OrderItem, OrderItemCustomization, OrderItemAddOn
from apps.orders.serializers import CartSerializer, AddToCartSerializer, OrderSerializer, OrderTrackingSerializer
from apps.menu.models import MenuItem, MenuItemCustomizationOption, MenuItemAddOn
from apps.restaurants.models import RestaurantStaffMember
from apps.users.models import SavedAddress
from decimal import Decimal


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing placed orders"""
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsCustomerUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOfOrder]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CUSTOMER':
            # Customers only see their own orders, excluding active carts
            return Order.objects.filter(customer=user).exclude(status='CART').select_related('restaurant').prefetch_related('items')
        elif user.role == 'RESTAURANT_OWNER':
            return Order.objects.filter(restaurant__owner=user).exclude(status='CART').select_related('restaurant').prefetch_related('items')
        elif user.role == 'RESTAURANT_STAFF':
            staff_member = RestaurantStaffMember.objects.filter(user=user).first()
            if staff_member:
                return Order.objects.filter(restaurant=staff_member.restaurant).exclude(status='CART').select_related('restaurant').prefetch_related('items')
            return Order.objects.none()
        elif user.role == 'SUPER_ADMIN':
            return Order.objects.exclude(status='CART').select_related('restaurant').prefetch_related('items')
        return Order.objects.none()

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def track(self, request, pk=None):
        """GET /api/v1/orders/{id}/track/ - Track order status"""
        order = self.get_object()
        serializer = OrderTrackingSerializer(order)
        return Response(serializer.data)


class CartViewSet(viewsets.ViewSet):
    """Shopping Cart endpoints for Customers (Step 3.3 & 3.4)"""
    permission_classes = [IsAuthenticated, IsCustomerUser]

    def get_cart(self, request):
        """Get or create the user's active cart"""
        cart, created = Order.objects.get_or_create(
            customer=request.user,
            status='CART'
        )
        return cart

    def list(self, request):
        """GET /api/v1/cart/ - Get current cart"""
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='items')
    def add_item(self, request):
        """POST /api/v1/cart/items/ - Add item to cart"""
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        menu_item = data['menu_item']
        quantity = data['quantity']
        
        cart = self.get_cart(request)
        
        # Enforce single restaurant per cart
        if cart.restaurant_id and cart.restaurant_id != menu_item.restaurant_id:
            return Response(
                {"error": "Your cart already contains items from another restaurant. Please clear your cart first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Assign restaurant to cart if empty
        if not cart.restaurant_id:
            cart.restaurant = menu_item.restaurant
            cart.save()

        # Calculate item price (base + customizations + addons)
        item_price = menu_item.price
        
        # Create OrderItem
        order_item = OrderItem.objects.create(
            order=cart,
            menu_item=menu_item,
            item_name=menu_item.name,
            item_price=item_price,
            quantity=quantity,
            special_instructions=data.get('special_instructions', '')
        )

        # Add Customizations
        if 'customization_option_ids' in data:
            for opt_id in data['customization_option_ids']:
                try:
                    opt = MenuItemCustomizationOption.objects.get(id=opt_id, customization__menu_item=menu_item)
                    OrderItemCustomization.objects.create(
                        order_item=order_item,
                        customization_name=opt.customization.name,
                        option_name=opt.name,
                        price_modifier=opt.price_modifier
                    )
                    item_price += opt.price_modifier
                except MenuItemCustomizationOption.DoesNotExist:
                    pass

        # Add Add-ons
        if 'addon_ids' in data:
            for addon_id in data['addon_ids']:
                try:
                    addon = MenuItemAddOn.objects.get(id=addon_id, menu_item=menu_item)
                    OrderItemAddOn.objects.create(
                        order_item=order_item,
                        addon_name=addon.name,
                        addon_price=addon.price
                    )
                    item_price += addon.price
                except MenuItemAddOn.DoesNotExist:
                    pass

        # Update order item price with modifiers and recalculate subtotal
        order_item.item_price = item_price
        order_item.save()
        order_item.calculate_subtotal()

        # Recalculate cart totals
        cart.calculate_totals()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'], url_path='items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """PATCH /api/v1/cart/items/{item_id}/ - Update quantity"""
        cart = self.get_cart(request)
        order_item = get_object_or_404(OrderItem, id=item_id, order=cart)
        
        quantity = request.data.get('quantity')
        if not quantity or int(quantity) < 1:
            return Response({"error": "Quantity must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)
        
        order_item.quantity = int(quantity)
        order_item.save()
        order_item.calculate_subtotal()
        cart.calculate_totals()
        
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """DELETE /api/v1/cart/items/{item_id}/ - Remove item from cart"""
        cart = self.get_cart(request)
        order_item = get_object_or_404(OrderItem, id=item_id, order=cart)
        
        order_item.delete()
        cart.calculate_totals()
        
        # If cart is empty, remove restaurant association
        if not cart.items.exists():
            cart.restaurant = None
            cart.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        """POST /api/v1/cart/checkout/ - Convert cart to a placed order (Step 3.4 Logic)"""
        cart = self.get_cart(request)
        
        if not cart.items.exists():
            return Response({"error": "Cannot checkout an empty cart"}, status=status.HTTP_400_BAD_REQUEST)
        
        order_type = request.data.get('order_type', 'PICKUP').upper()
        
        # Validate order type selection against restaurant offerings
        if order_type == 'PICKUP' and not cart.restaurant.allows_pickup:
            raise ValidationError("This restaurant does not accept pickup orders.")
        elif order_type == 'DELIVERY' and not cart.restaurant.allows_delivery:
            raise ValidationError("This restaurant does not accept delivery orders.")
        elif order_type == 'DINE_IN' and not cart.restaurant.allows_dine_in:
            raise ValidationError("This restaurant does not accept dine-in orders.")

        cart.status = 'PLACED'
        cart.order_type = order_type

        # Handle Order Type Specifics
        if order_type == 'DELIVERY':
            address_id = request.data.get('address_id')
            if not address_id:
                raise ValidationError({"address_id": "Address ID is required for delivery orders."})
            
            try:
                address = SavedAddress.objects.get(id=address_id, user=request.user)
            except SavedAddress.DoesNotExist:
                raise ValidationError({"address_id": "Invalid delivery address."})
                
            cart.delivery_address = address.address
            cart.delivery_city = address.city
            cart.delivery_state = address.state
            cart.delivery_country = address.country
            cart.delivery_postal_code = address.postal_code
            cart.delivery_latitude = address.latitude
            cart.delivery_longitude = address.longitude
            cart.delivery_instructions = request.data.get('delivery_instructions', '')

        elif order_type == 'PICKUP':
            pickup_time = request.data.get('pickup_time')
            if not pickup_time:
                raise ValidationError({"pickup_time": "Pickup time is required for pickup orders."})
            cart.pickup_time = pickup_time

        elif order_type == 'DINE_IN':
            table_number = request.data.get('table_number')
            if not table_number:
                raise ValidationError({"table_number": "Table number is required for dine-in orders."})
            cart.table_number = table_number
            cart.number_of_guests = request.data.get('number_of_guests', 1)

        cart.save()
        cart.calculate_totals()
        
        return Response({
            "message": "Order placed successfully!",
            "order_id": str(cart.id),
            "order_type": cart.order_type,
            "total_amount": str(cart.total_amount)
        }, status=status.HTTP_200_OK)