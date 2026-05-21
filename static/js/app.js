const state = {
    loggedIn: false,
    products: [],
    cart: [],
};

const userStatus = document.getElementById("user-status");
const loginForm = document.getElementById("login-form");
const loginMessage = document.getElementById("login-message");
const searchInput = document.getElementById("search-input");
const productsContainer = document.getElementById("products");
const cartContainer = document.getElementById("cart-items");
const cartTotal = document.getElementById("cart-total");
const checkoutMessage = document.getElementById("checkout-message");
const logoutButton = document.getElementById("logout-btn");

function formatCurrency(amount) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2,
    }).format(amount);
}

function setMessage(element, text, isError = false) {
    element.textContent = text;
    element.style.color = isError ? "#b5422c" : "#66717a";
}

function renderProducts(products) {
    productsContainer.innerHTML = "";

    if (!products.length) {
        productsContainer.innerHTML = "<p class='message'>No products found for this search.</p>";
        return;
    }

    products.forEach((product) => {
        const card = document.createElement("article");
        card.className = "product-item";
        card.innerHTML = `
            <div class="product-meta">
                <h3>${product.name}</h3>
                <span class="pill">${product.category}</span>
            </div>
            <p>${product.description}</p>
            <p class="price">${formatCurrency(product.price)}</p>
            <button data-id="${product.id}" class="add-to-cart-btn">Add to Cart</button>
        `;
        productsContainer.appendChild(card);
    });

    document.querySelectorAll(".add-to-cart-btn").forEach((button) => {
        button.addEventListener("click", async (event) => {
            const productId = Number(event.target.dataset.id);
            await addToCart(productId);
        });
    });
}

function renderCart(items) {
    state.cart = items;
    cartContainer.innerHTML = "";

    if (!items.length) {
        cartContainer.innerHTML = "<p class='message'>Your cart is empty.</p>";
        cartTotal.textContent = formatCurrency(0);
        return;
    }

    let total = 0;
    items.forEach((item) => {
        total += item.line_total;
        const row = document.createElement("article");
        row.className = "cart-item";
        row.innerHTML = `
            <div class="cart-meta">
                <div>
                    <h3>${item.name}</h3>
                    <p>Qty: ${item.quantity}</p>
                </div>
                <strong>${formatCurrency(item.line_total)}</strong>
            </div>
        `;
        cartContainer.appendChild(row);
    });

    cartTotal.textContent = formatCurrency(total);
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
        },
        credentials: "same-origin",
        ...options,
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "Request failed");
    }
    return data;
}

async function loadProducts() {
    if (!state.loggedIn) {
        return;
    }
    try {
        const query = searchInput.value.trim();
        const suffix = query ? `?search=${encodeURIComponent(query)}` : "";
        const data = await apiRequest(`/products${suffix}`);
        state.products = data.products;
        renderProducts(data.products);
    } catch (error) {
        renderProducts([]);
        setMessage(loginMessage, error.message, true);
    }
}

async function loadCart() {
    if (!state.loggedIn) {
        renderCart([]);
        return;
    }
    const data = await apiRequest("/cart");
    renderCart(data.items);
}

async function addToCart(productId) {
    try {
        await apiRequest("/cart", {
            method: "POST",
            body: JSON.stringify({ product_id: productId, quantity: 1 }),
        });
        setMessage(checkoutMessage, "Product added to cart.");
        await loadCart();
    } catch (error) {
        setMessage(checkoutMessage, error.message, true);
    }
}

async function login(username, password) {
    const data = await apiRequest("/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
    });
    state.loggedIn = true;
    userStatus.textContent = `Logged in as ${data.username}`;
    logoutButton.hidden = false;
    setMessage(loginMessage, data.message);
    await loadProducts();
    await loadCart();
}

async function logout() {
    await apiRequest("/logout", { method: "POST" });
    state.loggedIn = false;
    userStatus.textContent = "Not logged in";
    logoutButton.hidden = true;
    renderProducts([]);
    renderCart([]);
    setMessage(loginMessage, "Logged out.");
}

async function checkout() {
    try {
        const data = await apiRequest("/checkout", { method: "POST" });
        setMessage(checkoutMessage, `${data.message}. Order status: ${data.order_summary.status}.`);
        await loadCart();
    } catch (error) {
        setMessage(checkoutMessage, error.message, true);
    }
}

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    try {
        await login(username, password);
    } catch (error) {
        state.loggedIn = false;
        setMessage(loginMessage, error.message, true);
    }
});

document.getElementById("search-btn").addEventListener("click", loadProducts);
document.getElementById("checkout-btn").addEventListener("click", checkout);
logoutButton.addEventListener("click", logout);

renderProducts([]);
renderCart([]);
