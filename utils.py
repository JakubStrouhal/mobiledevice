from datetime import datetime
from models import DeviceAssignment

def generate_protocol_number():
    """Generate a unique protocol number based on current timestamp and sequence"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    count = DeviceAssignment.query.filter(
        DeviceAssignment.protocol_number.like(f"{timestamp}%")
    ).count()
    return f"PRO-{timestamp}-{count + 1:03d}"

def format_currency(amount, currency='CZK'):
    """Format currency amount with proper spacing and symbol"""
    if currency == 'CZK':
        return f"{amount:,.0f} Kč"
    return f"{amount:,.2f} {currency}"

def get_device_status_badge(status):
    """Return appropriate Bootstrap badge class for device status"""
    status_classes = {
        'active': 'success',
        'inactive': 'secondary',
        'maintenance': 'warning',
        'retired': 'danger'
    }
    return status_classes.get(status, 'secondary')
