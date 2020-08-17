let closeAlertBtn = document.querySelector('#close-alert');

if (closeAlertBtn) {
    closeAlertBtn.addEventListener('click', closeAlert);
}

function closeAlert(){
    this.parentElement.style.display = 'none';
}
