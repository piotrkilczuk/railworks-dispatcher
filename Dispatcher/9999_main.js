function handleClick() {
    if (this.classList.length > 1) {
        snack.wrap(this).removeClass('collapsed');
    } else {
        snack.wrap(this).addClass('collapsed');
    }
}

snack.wrap('article').each(function (element, index) {
    snack.listener({node: element, event: 'click'}, handleClick);
});