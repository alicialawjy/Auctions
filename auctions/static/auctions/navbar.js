document.addEventListener('DOMContentLoaded', function() {
    const button = document.querySelector('#category_nav');
    button.onclick = function () {
        if (button.dataset.show === 'hide') {
            button.dataset.show = 'show';
            document.querySelector('#category_dropdown').style.display = 'block';
        }
        else {
            button.dataset.show = 'hide';
            document.querySelector('#category_dropdown').style.display = 'none';
        }
    };
    window.onclick = function (e) {
        if (!e.target.matches('#category_nav')) {
            button.dataset.show = 'hide';
            document.querySelector('#category_dropdown').style.display = 'none';
        }
        
    }
});