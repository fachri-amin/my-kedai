let registerAnchor = document.getElementById("register-anchor");

registerAnchor.addEventListener("click", function (e) {
    e.preventDefault();
});

let updateBtns = document.getElementsByClassName("update-cart");

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener("click", function () {
        let productId = this.dataset.product;
        let action = this.dataset.action;

        if (user === "AnonymousUser") {
            if (this.classList.contains("chg-quantity")) {
                let urltotal = this.dataset.urltotal;
                addCookieItem(productId, action, this);
                updateTotal(urltotal);
            } else {
                addCookieItem(productId, action, this);
            }
        } else {
            if (this.classList.contains("chg-quantity")) {
                let urltotal = this.dataset.urltotal;
                updateQuantity(productId, action, this.dataset.url, this);
                updateTotal(urltotal);
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

function addCookieItem(productId, action, el) {
    if (action == "add") {
        if (!cart[productId]) {
            cart[productId] = {
                quantity: 1,
            };
        } else {
            cart[productId]["quantity"] += 1;
            if (el.classList.contains('chg-quantity')) {
                document.querySelector(`p[data-product='${productId}']`).innerHTML = cart[productId]["quantity"];
                fetch('')
            }
        }
    }

    if (action == "remove") {
        cart[productId]["quantity"] -= 1;
        if (el.classList.contains('chg-quantity')) {
            document.querySelector(`p[data-product='${productId}']`).innerHTML = cart[productId]["quantity"];
        }
        if (cart[productId]["quantity"] <= 0) {
            if (el.classList.contains('chg-quantity')) {
                document.querySelector(`div[data-product='${productId}']`).remove();
            }
            delete cart[productId];
        }
    }

    document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";

    var total_cart = 0;

    Object.values(cart).forEach(function (item) {
        total_cart += item.quantity;
    });

    // console.log(total_cart);
    let cart_total = document.getElementById("cart-total");
    try {
        document.getElementById("cart-alert").classList.remove("hidden");
        setTimeout(function () {
            document.getElementById("cart-alert").classList.add("hidden");
        }, 3000);
    } catch {}
    cart_total.innerHTML = total_cart;

    // location.reload();
}

let detailBtns = document.querySelectorAll('.btn-detail');

detailBtns.forEach(function (e) {

    e.addEventListener('click', function () {
        let productId = this.dataset.product
        let url = this.dataset.url;

        productDetail = getProductDetail(productId, url);
    })
});

function getProductDetail(productId, url) {
    fetch(url + '?id=' + productId)
        .then((response) => response.json())
        .then((data) => {
            let title = document.getElementById('detail-title');
            let description = document.getElementById('detail-description');
            let price = document.getElementById('detail-price');
            let image = document.getElementById('detail-image');
            let detailAdd = document.getElementById('detail-to-add');

            let reverse = data[0].fields.price.toString().split('').reverse().join(''),
                priceData = reverse.match(/\d{1,3}/g);
            priceData = priceData.join('.').split('').reverse().join('');

            title.innerHTML = data[0].fields.name;
            description.innerHTML = data[0].fields.description;
            price.innerHTML = 'Rp. ' + priceData;
            image.src = '/media/' + data[0].fields.image;
            detailAdd.dataset.product = data[0].pk;
            console.log(data);
        })
}

function updateTotal(url) {
    fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify(cart),
        })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            let reverse = data.total_price.toString().split('').reverse().join(''),
                priceData = reverse.match(/\d{1,3}/g);
            priceData = priceData.join('.').split('').reverse().join('');

            document.getElementById('total-price').innerHTML = priceData;
            document.getElementById('items').innerHTML = data.total_item;
        });
}