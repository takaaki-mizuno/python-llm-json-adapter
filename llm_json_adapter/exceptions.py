class RetryableError(Exception):
    pass


class ExceededMaxRetryCountError(Exception):
    pass
