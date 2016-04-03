(function($) {
    $(document).ready(function() {
        $('form:has(.contenteditable)').submit(function(e) {
            $(this).find('.contenteditable').each(function() {
                if (input_selector = $(this).data('target-input')) {
                    $(input_selector).val($(this).text());
                }
            });
        })
    });
})(django.jQuery);
