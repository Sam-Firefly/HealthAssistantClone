document.querySelector('.send-button').addEventListener('click', () => {
    const input = document.querySelector('input[type="text"]');
    if (input.value) {
        alert(`You entered: ${input.value}`);
        input.value = '';
    }
});
