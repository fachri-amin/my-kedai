let registerAnchor = document.getElementById('register-anchor')

registerAnchor.addEventListener('click', function (e) {
    e.preventDefault()
})

let updateBtns = document.getElementsByClassName("update-cart");

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener("click", function () {
        let productId = this.dataset.product;
        let action = this.dataset.action;

        if (user === "AnonymousUser") {
            addCookieItem(productId, action, this.dataset.url);
        } else {
            if (this.classList.contains("chg-quantity")) {
                updateQuantity(productId, action, this.dataset.url, this);
            } else {
                updateUserOrder(productId, action, this.dataset.url);
            }
        }
    });
}

function updateUserOrder(productId, action, url) {
    fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({
                productId: productId,
                action: action,
            }),
        })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            let cart_total = document.getElementById("cart-total");
            cart_total.innerHTML = data.total_item;
            document.getElementById("cart-alert").classList.remove("hidden");
            setTimeout(function () {
                document.getElementById("cart-alert").classList.add("hidden");
            }, 3000);
        });
}

function updateQuantity(productId, action, url, element) {
    fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({
                productId: productId,
                action: action,
            }),
        })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            arrowParent = element.parentElement;
            quantityParent = arrowParent.parentElement;
            productParent = quantityParent.parentElement;
            document.getElementById("items").innerHTML = data.total_item;
            document.getElementById("total-price").innerHTML = `Rp ${data.total}`;
            document.getElementById("cart-total").innerHTML = data.total_item;
            if (data.quantity == 0) {
                productParent.remove();
            } else {
                quantityParent.firstElementChild.innerHTML = data.quantity;
                productParent.lastElementChild.innerHTML = data.item_price;
            }
        });
}

function addCookieItem(productId, action, url) {
    if (action == "add") {
        if (!cart[productId]) {
            cart[productId] = {
                'quantity': 1,
            };
        } else {
            cart[productId]["quantity"] += 1;
        }
    }

    if (action == "remove") {
        cart[productId]["quantity"] -= 1;
        if (cart[productId]["quantity"]) {
            delete cart[productId];
        }
    }

    document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";

    location.reload();
    // updateUserOrder(productId, action, url);
    // let cart_total = document.getElementById('cart-total');
    // cart_total.innerHTML = data.total_item;
}