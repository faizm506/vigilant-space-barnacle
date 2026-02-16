from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # 1. Columns shown in the main list view
    # We added tour_price and payment_status for quick oversight
    list_display = ('booking_id', 'customer_name', 'tour_price', 'payment_status', 'created_at')
    
    # 2. Sidebar Filters
    # Allows the manager to quickly see all "Paid" or "Pending" bookings
    list_filter = ('payment_status', 'created_at')
    
    # 3. Search Bar
    # Search by Name, UID, or even Address
    search_fields = ('customer_name', 'booking_id', 'address')
    
    # 4. Read-only fields
    # Prevents accidental editing of the Branded UID or timestamps
    readonly_fields = ('booking_id', 'created_at', 'updated_at')
    
    # 5. Detail View Organization (Fieldsets)
    fieldsets = (
        ('Branding & ID', {
            'fields': ('booking_id', 'created_at')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'address', 'total_members')
        }),
        ('Financials', {
            'fields': ('tour_price', 'payment_status'),
            'description': "Manage the tour cost and current payment tracking."
        }),
        ('Documentation', {
            'fields': ('passport_photo',),
        }),
        ('Custom Data', {
            'classes': ('collapse',), # This section is hidden by default to keep it clean
            'fields': ('additional_info',),
            'description': "Raw JSON data for concierge preferences."
        }),
    )

    # Optional: Adds a "Mark as Paid" bulk action in the admin list
    actions = ['make_paid']

    @admin.action(description='Mark selected bookings as Paid')
    def make_paid(self, request, queryset):
        queryset.update(payment_status='Paid')