let closeAlertBtns = document.querySelectorAll('#close-alert');

if (closeAlertBtns) {
    closeAlertBtns.forEach((closeAlertBtn)=>{
        closeAlertBtn.addEventListener('click', closeAlert);
    });
}

function closeAlert(){
    this.parentElement.style.display = 'none';
}
