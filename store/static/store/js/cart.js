let updateBtns = document.getElementsByClassName("update-cart");

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener("click", function () {
        let productId = this.dataset.product;
        let action = this.dataset.action;

        console.log("productId:", productId, "action:", action);

        console.log("USER", user);
        if (user === "AnonymousUser") {
            console.log("not logged in");
        } else {
            updateUserOrder(productId, action, this.dataset.url);
        }
    });
}

function updateUserOrder(productId, action, url) {
    console.log('User Logged in, sending data...');

    fetch(url, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                'productId': productId,
                'action': action
            })
        })
        .then(response => {
            return response.json();
        })
        .then(data => {
            console.log(data);
        })
}