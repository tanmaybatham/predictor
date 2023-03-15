
function hideErrorMessage() {
    const errorMessageDiv = document.getElementById("errorMessageDiv");
    errorMessageDiv.innerHTML= null;
}

// Call the hideDiv function after 5 seconds
setTimeout(hideErrorMessage, 3000);