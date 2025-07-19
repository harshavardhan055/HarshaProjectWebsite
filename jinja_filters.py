from datetime import datetime
from app_init import app # Changed import from app to app_init

@app.template_filter('now')
def filter_now(format_string):
    """Return the current date/time formatted according to the format specified"""
    return datetime.now().strftime(format_string)

@app.template_filter('format_date')
def filter_format_date(date, format_string="%B %d, %Y"):
    """Format a date according to the specified format"""
    if isinstance(date, datetime):
        return date.strftime(format_string)
    return date

@app.template_filter('truncate_html')
def filter_truncate_html(text, length=100, ellipsis='...'):
    """Truncate HTML text to a certain length while keeping HTML tags"""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length] + ellipsis

@app.template_filter('nl2br')
def filter_nl2br(text):
    """Convert newlines to HTML line breaks"""
    if not text:
        return ""
    return text.replace('\n', '<br>')

# Register the filters with Flask (already registered via decorator, but can keep these for clarity)
# app.jinja_env.filters['now'] = filter_now
# app.jinja_env.filters['format_date'] = filter_format_date
# app.jinja_env.filters['truncate_html'] = filter_truncate_html
# app.jinja_env.filters['nl2br'] = filter_nl2br
