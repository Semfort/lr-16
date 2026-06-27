document.addEventListener('DOMContentLoaded', function () {

  // ─── Утилиты ───────────────────────────────────────────────

  function getCsrfToken() {
    return document.cookie
      .split(';')
      .map(c => c.trim())
      .find(c => c.startsWith('csrftoken='))
      ?.split('=')[1] || '';
  }

  function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:9999;min-width:280px;';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible shadow fade show`;
    toast.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  }

  function showSpinner(container) {
    container.innerHTML = `
      <div class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="mt-2 text-muted">Загружаем товары...</p>
      </div>`;
  }

  function renderProducts(products, container) {
    if (products.length === 0) {
      container.innerHTML = `
        <div class="text-center py-5">
          <h4 class="text-muted">Товары не найдены</h4>
          <p>Попробуйте изменить параметры фильтрации.</p>
        </div>`;
      return;
    }

    const row = document.createElement('div');
    row.className = 'row';

    products.forEach(product => {
      const inStock = product.quantity_in_stock > 0;
      const imgHtml = product.image
        ? `<img src="${product.image}" class="card-img-top" style="height:200px;object-fit:cover;" alt="${product.name}">`
        : `<div class="bg-secondary text-white d-flex align-items-center justify-content-center" style="height:200px;">Нет фото</div>`;

      const col = document.createElement('div');
      col.className = 'col-sm-6 col-md-4 mb-4';
      col.innerHTML = `
        <div class="card h-100 shadow-sm">
          ${imgHtml}
          <div class="card-body d-flex flex-column">
            <h6 class="card-title">${product.name}</h6>
            <p class="text-muted small mb-1">${product.category}</p>
            <p class="text-primary fw-bold mt-auto mb-2">${product.price} руб.</p>
            <span class="badge ${inStock ? 'bg-success' : 'bg-danger'} mb-2">
              ${inStock ? 'В наличии' : 'Нет в наличии'}
            </span>
            <div class="d-flex gap-2">
              <a href="${product.detail_url}" class="btn btn-outline-primary btn-sm flex-grow-1">Подробнее</a>
              <button
                class="btn btn-primary btn-sm flex-grow-1 btn-add-to-cart"
                data-product-id="${product.id}"
                data-url="${product.add_to_cart_url}"
                ${!inStock ? 'disabled' : ''}>
                В корзину
              </button>
            </div>
          </div>
        </div>`;
      row.appendChild(col);
    });

    container.innerHTML = '';
    container.appendChild(row);
  }

  // ─── Загрузка товаров из API ────────────────────────────────

  async function loadProducts() {
    const container = document.getElementById('products-container');
    if (!container) return;

    showSpinner(container);

    const params = new URLSearchParams(window.location.search);

    try {
      const response = await fetch(`/api/products/?${params.toString()}`);
      if (!response.ok) throw new Error(`Ошибка сервера: ${response.status}`);
      const data = await response.json();
      renderProducts(data.products, container);
    } catch (error) {
      container.innerHTML = `
        <div class="alert alert-danger">
          <strong>Ошибка загрузки товаров.</strong> Попробуйте обновить страницу.
        </div>`;
    }
  }

  // ─── Добавление в корзину ───────────────────────────────────

  async function addToCart(productId) {
    try {
      const response = await fetch('/api/cart/add/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({ product_id: productId }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        showToast(data.message, 'success');
      } else {
        showToast(data.message || 'Не удалось добавить товар', 'danger');
      }
    } catch (error) {
      showToast('Ошибка соединения с сервером', 'danger');
    }
  }

  // ─── Делегирование клика на кнопки "В корзину" ─────────────

  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.btn-add-to-cart');
    if (!btn || btn.disabled) return;
    const productId = btn.dataset.productId;
    addToCart(productId);
  });

  // ─── Запуск ─────────────────────────────────────────────────

  loadProducts();
});