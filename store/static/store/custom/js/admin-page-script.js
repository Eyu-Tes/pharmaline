//toggle sidebar
const toggleBtn = document.querySelector('#toggle-sidebar');
const pageWrapper = document.querySelector('.page-wrapper');

toggleBtn.addEventListener('click', () => {
    pageWrapper.classList.toggle("toggled");
});
