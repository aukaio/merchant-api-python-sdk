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
    Required('user_id'): basestring,
    'roles': [Any('user', 'superuser')],
    'netmask': basestring,
    'secret': All(basestring, Length(min=8, max=64)),
    'pubkey': basestring
})

update_user_validator = Schema({
    Required('user_id'): basestring,
    'roles': [Any('user', 'superuser')],
    'netmask': basestring,
    'secret': All(basestring, Length(min=8, max=64)),
    'pubkey': basestring
})

create_pos_validator = Schema({
    Required('name'): basestring,
    Required('pos_type'): basestring,
    Required('pos_id'): basestring,
    'location': {'latitude': float,
                 'longitude': float,
                 'accuracy': float}
})

create_shortlink_validator = Schema({
    'callback_uri': basestring,
    'description': basestring,
    'serial_number': basestring
})

update_pos_validator = Schema({
    Required('pos_id'): basestring,
    Required('name'): basestring,
    Required('pos_type'): basestring,
    'location': {'latitude': float,
                 'longitude': float,
                 'accuracy': float}
})

create_payment_request_validator = Schema({
    'ledger': basestring,
    'display_message_uri': basestring,
    'callback_uri': basestring,
    Required('customer'): All(basestring, Length(max=100)),
    Required('currency'): All(basestring, Length(min=3, max=3)),
    Required('amount'): basestring,
    'additional_amount': basestring,
    'additional_edit': bool,
    Required('allow_credit'): bool,
    Required('pos_id'): basestring,
    Required('pos_tid'): basestring,
    'text': basestring,
    Required('action'): Any('auth', 'sale', 'AUTH', 'SALE'),
    Required('expires_in'): All(int, Range(min=0, max=2592000)),
})

update_payment_request_validator = Schema({
    'tid': basestring,
    'ledger': basestring,
    'display_message_uri': basestring,
    'callback_uri': basestring,
    'currency': All(basestring, Length(min=3, max=3)),
    'amount': basestring,
    'additional_amount': basestring,
    'capture_id': basestring,
    'refund_id': basestring,
    'text': basestring,
    'action': Any('reauth', 'capture', 'abort', 'release', 'refund',
                  'REAUTH', 'CAPTURE', 'ABORT', 'RELEASE', 'REFUND'),
})

update_ticket_validator = Schema({
    Required('tid'): basestring,
    'tickets': list,
})

update_shortlink_validator = Schema({
    Required('shortlink_id'): basestring,
    'callback_uri': basestring,
    'description': basestring
})

create_ledger_validator = Schema({
    Required('currency'): basestring,
    'description': basestring
})

update_ledger_validator = Schema({
    Required('ledger_id'): basestring,
    'description': basestring
})

close_report_validator = Schema({
    Required('ledger_id'): basestring,
    Required('report_id'): basestring,
    'callback_uri': basestring,
})

create_permission_request_validator = Schema({
    'ledger': basestring,
    Required('customer'): All(basestring, Length(max=100)),
    Required('pos_id'): basestring,
    Required('pos_tid'): basestring,
    'text': basestring,
    'callback_uri': basestring,
    Required('scope'): basestring,
    'expires_in': All(int, Range(min=0, max=2592000)),
})
