from functools import wraps
from voluptuous import Schema, Required, Any, All, Length, Range


def validate_input(function):
    """Decorator that validates the kwargs of the function passed to it."""
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            name = function.__name__ + '_validator'  # find validator name
            globals()[name](kwargs)  # call validation function
            return function(*args, **kwargs)
        except KeyError:
            raise Exception("Could not find validation schema for the"
                            " function " + function.__name__)
    return wrapper

create_user_validator = Schema({
    Required('user_id'): str,
    'roles': [Any('user', 'superuser')],
    'netmask': str,
    'secret': All(str, Length(min=8, max=64)),
    'pubkey': str
})

update_user_validator = Schema({
    Required('user_id'): str,
    'roles': [Any('user', 'superuser')],
    'netmask': str,
    'secret': All(str, Length(min=8, max=64)),
    'pubkey': str
})

create_pos_validator = Schema({
    Required('name'): str,
    Required('pos_type'): str,
    Required('pos_id'): str,
    'location': {'latitude': float,
                 'longitude': float,
                 'accuracy': float}
})

update_pos_validator = Schema({
    Required('pos_id'): str,
    Required('name'): str,
    Required('pos_type'): str,
    'location': {'latitude': float,
                 'longitude': float,
                 'accuracy': float}
})

create_payment_request_validator = Schema({
    'ledger': str,
    'display_message_uri': str,
    'callback_uri': str,
    Required('customer'): All(str, Length(max=100)),
    Required('currency'): All(str, Length(min=3, max=3)),
    Required('amount'): str,
    'additional_amount': All(float, Range(min=0)),
    'additional_edit': bool,
    Required('allow_credit'): bool,
    Required('pos_id'): str,
    Required('pos_tid'): str,
    'text': str,
    Required('action'): Any('auth', 'sale', 'AUTH', 'SALE'),
    Required('expires_in'): All(int, Range(min=0, max=2592000)),
})

update_payment_request_validator = Schema({
    Required('tid'): str,
    'ledger': str,
    'display_message_uri': str,
    'callback_uri': str,
    'currency': All(str, Length(min=3, max=3)),
    'amount': str,
    'additional_amount': All(float, Range(min=0)),
    'capture_id': str,
    'action': Any('reauth', 'capture', 'abort', 'release',
                  'REAUTH', 'CAPTURE', 'ABORT', 'RELEASE'),
})

update_ticket_validator = Schema({
    Required('tid'): str,
    'tickets': list,
})

create_shortlink_validator = Schema({
    'callback_uri': str,
    'description': str,
    'serial_number': str
})

update_shortlink_validator = Schema({
    Required('shortlink_id'): str,
    'callback_uri': str,
    'description': str
})

create_ledger_validator = Schema({
    Required('currency'): str,
    'description': str
})

update_ledger_validator = Schema({
    Required('ledger_id'): str,
    'description': str
})

close_report_validator = Schema({
    Required('ledger_id'): str,
    Required('report_id'): str,
    'callback_uri': str,
})

create_permission_request_validator = Schema({
    'ledger': str,
    Required('customer'): All(str, Length(max=100)),
    Required('pos_id'): str,
    Required('pos_tid'): str,
    'text': str,
    'callback_uri': str,
    Required('scope'): str,
    'expires_in': All(int, Range(min=0, max=2592000)),
})
