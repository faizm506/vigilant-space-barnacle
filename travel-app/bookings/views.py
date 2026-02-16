import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Booking # We will create this model next
from django.db.models import Sum, Q


@login_required
def dashboard(request):
    query = request.GET.get('search')
    
    if query:
        bookings = Booking.objects.filter(
            Q(customer_name__icontains=query) | Q(booking_id__icontains=query)
        ).order_by('-id')
    else:
        bookings = Booking.objects.all().order_by('-id')

    # Calculate Totals
    total_travelers = bookings.aggregate(Sum('total_members'))['total_members__sum'] or 0
    unpaid_count = bookings.exclude(payment_status='Paid').count()

    context = {
        'bookings': bookings,
        'total_travelers': total_travelers,
        'unpaid_count': unpaid_count,
    }

    # THE FIX: If the request is from HTMX, render ONLY the rows
    if request.headers.get('HX-Request'):
        return render(request, 'bookings/partials/booking_rows.html', context)
    
    # Otherwise, render the full dashboard page
    return render(request, 'bookings/dashboard.html', context)

@login_required
def new_booking(request):
    if request.method == 'POST':
        # 1. Capture the raw inputs
        price_per_person = float(request.POST.get('tour_price', 0) or 0)
        members_count = int(request.POST.get('total_members', 1) or 1)

        # 2. Automatically calculate the Total Price
        calculated_total = price_per_person * members_count

        # 3. Create the record
        booking = Booking.objects.create(
            customer_name=request.POST.get('customer_name'),
            address=request.POST.get('address'),
            total_members=members_count,
            passport_photo=request.FILES.get('passport_photo'),
            tour_price=calculated_total, # Saves the full total (e.g., 45000 * 2)
            payment_status=request.POST.get('payment_status'),
            additional_info={
                "Price Per Person": f"₹{price_per_person}",
                "Meal Preference": request.POST.get('meal_pref'),
                "Hotel Grade": request.POST.get('hotel_stars')
            }
        )
        return redirect('dashboard')
    return render(request, 'bookings/booking_form.html')


from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from django.http import HttpResponse

@login_required
def export_bookings_csv(request):
    # Create workbook and active sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Razak and Sons Bookings"

    # 1. Define Premium Headers
    headers = ['Booking UID', 'Customer Name', 'Total Members', 'Package Price', 'Payment Status', 'Date Booked']
    ws.append(headers)

    # Styling the header row (Bold, White Text, Navy Background)
    header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # 2. Add Data Rows
    bookings = Booking.objects.all().order_by('-created_at')
    for b in bookings:
        ws.append([
            b.booking_id,
            b.customer_name,
            b.total_members,
            float(b.tour_price), # Ensure it's a number for Excel math
            b.payment_status,
            b.created_at.replace(tzinfo=None) # Excel doesn't like timezones
        ])

    # 3. Auto-Adjust Column Widths
    # This loop calculates the length of the longest value in each column
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # 4. Return the response as an Excel file
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="Razak_Sons_Bookings.xlsx"'
    
    wb.save(response)
    return response

from django.shortcuts import render, get_object_or_404

@login_required
def booking_detail(request, booking_id):
    # This fetches the specific booking or shows a 404 error if not found
    booking = get_object_or_404(Booking, booking_id=booking_id)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    if request.method == 'POST':
        customer_name = booking.customer_name
        booking.delete()
        # Adding a success message for the manager
        messages.success(request, f"Booking for {customer_name} has been successfully removed.")
    return redirect('dashboard')



