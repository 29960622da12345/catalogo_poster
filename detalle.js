let allProductos = [], allCategorias = [], allSeries = [];
let productoActual = null;
let precioCalculado = 0;

function getCachedData() {
    try { const raw = sessionStorage.getItem('pp_data'); if (raw) return JSON.parse(raw); } catch (e) { /* */ }
    return null;
}
function setCachedData(data) {
    try { sessionStorage.setItem('pp_data', JSON.stringify(data)); } catch (e) { /* */ }
}

function openDrawer() {
    document.getElementById('drawer-menu').classList.add('open');
    document.getElementById('drawer-overlay').classList.add('open');
    document.getElementById('hamburger-btn').classList.add('active');
    document.body.style.overflow = 'hidden';
}
function closeDrawer() {
    document.getElementById('drawer-menu').classList.remove('open');
    document.getElementById('drawer-overlay').classList.remove('open');
    document.getElementById('hamburger-btn').classList.remove('active');
    document.body.style.overflow = '';
}
function toggleDrawer() {
    if (document.getElementById('drawer-menu').classList.contains('open')) closeDrawer();
    else openDrawer();
}

window.toggleSearchMobile = () => {
    if (!window.matchMedia('(max-width: 768px)').matches) return;
    const overlay = document.getElementById('search-mobile-overlay');
    const input = document.getElementById('search-mobile-input');
    const isOpen = overlay.classList.toggle('open');
    if (isOpen) input.focus(); else input.value = '';
};

function extraerNumeroPrecio(precioStr) {
    if (!precioStr) return 0;
    const match = precioStr.replace(/[^0-9.,]/g, '').replace(',', '.');
    const num = parseFloat(match);
    return isNaN(num) ? 0 : num;
}

function formatearPrecio(num) {
    return '$' + num.toFixed(2);
}

async function cargarDatos() {
    try {
        let data = getCachedData();
        if (!data) {
            const r = await fetch('data.json');
            if (r.ok) { data = await r.json(); setCachedData(data); }
        }
        if (data) {
            allCategorias = data.categorias || [];
            allSeries = data.series || [];
            allProductos = data.productos || [];
        }
    } catch (e) {
        console.error('Error al cargar datos:', e);
    }
}

async function cargarProducto() {
    const params = new URLSearchParams(window.location.search);
    const idProducto = params.get('id');

    if (!idProducto) {
        document.getElementById('producto-info').innerHTML = '<p style="color:var(--text-secondary);text-align:center;padding:60px 0;grid-column:1/-1;">Producto no especificado.</p>';
        return;
    }

    if (!allProductos.length) await cargarDatos();

    productoActual = allProductos.find(p => p.ID == idProducto);

    if (!productoActual) {
        document.getElementById('producto-info').innerHTML = '<p style="color:var(--text-secondary);text-align:center;padding:60px 0;grid-column:1/-1;">Producto no encontrado.</p>';
        return;
    }

    document.getElementById('product-img-zoom').src = productoActual.URL_Imagen;
    document.getElementById('product-img-zoom').alt = productoActual.Nombre;
    document.getElementById('product-img-mockup').src = productoActual.URL_Imagen;
    document.getElementById('product-img-mockup').alt = productoActual.Nombre;
    document.getElementById('product-cat').textContent = productoActual.Categoria_Nombre || 'Categoría';
    document.getElementById('product-title').textContent = productoActual.Nombre;


    actualizarPrecio();
    cargarRelacionados(allProductos);

    if (productoActual.Categoria_ID) {
        const cat = allCategorias.find(c => c.ID == productoActual.Categoria_ID);
        if (cat) document.getElementById('product-cat').textContent = cat.Nombre;
    }
}

const tamanoBtn = document.querySelector('.tamano-btn');

function actualizarPrecio() {
    if (!productoActual) return;
    const precioBase = extraerNumeroPrecio(productoActual.Precio);
    precioCalculado = precioBase;
    document.getElementById('product-price').textContent = formatearPrecio(precioCalculado);
}

tamanoBtn.addEventListener('click', () => {
    tamanoBtn.classList.toggle('active');
});

const qtyInput = document.getElementById('quantity-input');
document.getElementById('btn-minus').addEventListener('click', () => {
    let val = parseInt(qtyInput.value);
    if (val > 1) qtyInput.value = val - 1;
});
document.getElementById('btn-plus').addEventListener('click', () => {
    let val = parseInt(qtyInput.value);
    qtyInput.value = val + 1;
});

const zoomContainer = document.getElementById('zoom-container');
const productImgZoom = document.getElementById('product-img-zoom');

zoomContainer.addEventListener('mousemove', (e) => {
    const rect = zoomContainer.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    productImgZoom.style.transformOrigin = x + '% ' + y + '%';
    productImgZoom.style.transform = 'scale(1.8)';
});

zoomContainer.addEventListener('mouseleave', () => {
    productImgZoom.style.transformOrigin = 'center center';
    productImgZoom.style.transform = 'scale(1)';
});

const escenarioInterior = document.getElementById('escenario-interior');

escenarioInterior.addEventListener('mousemove', (e) => {
    const rect = escenarioInterior.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    escenarioInterior.style.transformOrigin = x + '% ' + y + '%';
    escenarioInterior.style.transform = 'scale(1.6)';
});

escenarioInterior.addEventListener('mouseleave', () => {
    escenarioInterior.style.transformOrigin = 'center center';
    escenarioInterior.style.transform = 'scale(1)';
});

function cargarRelacionados(todosProductos) {
    const contenedor = document.getElementById('related-products-container');
    contenedor.innerHTML = '';

    if (!productoActual) return;

    const relacionados = todosProductos.filter(p =>
        p.Serie_ID === productoActual.Serie_ID &&
        p.ID !== productoActual.ID
    );

    if (!relacionados.length) {
        contenedor.innerHTML = '<p style="color:var(--text-secondary);">No hay más diseños en esta colección.</p>';
        return;
    }

    relacionados.forEach(p => {
        const card = document.createElement('a');
        card.className = 'related-card';
        card.href = 'detalle.html?id=' + p.ID;
        card.innerHTML =
            '<img src="' + p.URL_Imagen + '" loading="lazy" onerror="this.src=\'https://placehold.co/600x800/2D3D33/F5F2ED?text=Error\'" alt="' + p.Nombre + '">' +
            '<div class="related-card-info">' +
                '<div class="related-card-title">' + p.Nombre + '</div>' +
                '<div class="related-card-price">' + (p.Precio || '') + '</div>' +
            '</div>';
        contenedor.appendChild(card);
    });
}

document.querySelectorAll('.view-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.view-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById('view-' + tab.dataset.view).classList.add('active');
    });
});

function actualizarContadorCarrito() {
    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const total = carrito.reduce((sum, item) => sum + item.cantidad, 0);
    document.getElementById('cart-counter').textContent = total;
}

document.getElementById('add-to-cart').addEventListener('click', () => {
    if (!productoActual) return;
    const cantidad = parseInt(qtyInput.value);

    const itemCarrito = {
        id: productoActual.ID,
        titulo: productoActual.Nombre,
        imagen: productoActual.URL_Imagen,
        precioFinal: precioCalculado,
        cantidad: cantidad,
        opciones: { tamaño: '30cm x 40cm', marco: 'Solo Lámina' }
    };

    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];

    const indexExistente = carrito.findIndex(item =>
        item.id === itemCarrito.id &&
        item.opciones.tamaño === itemCarrito.opciones.tamaño &&
        item.opciones.marco === itemCarrito.opciones.marco
    );

    if (indexExistente > -1) {
        carrito[indexExistente].cantidad += cantidad;
    } else {
        carrito.push(itemCarrito);
    }

    localStorage.setItem('carrito', JSON.stringify(carrito));
    actualizarContadorCarrito();

    const btn = document.getElementById('add-to-cart');
    btn.textContent = '✓ Agregado';
    btn.style.background = '#22c55e';
});

function cargarNav() {
    const nav = document.getElementById('nav-categorias');
    if (!nav) return;
    const drawerNav = document.getElementById('drawer-nav');
    let data = getCachedData();
    if (data && data.categorias) {
        nav.innerHTML = '<a href="index.html">Todo</a>';
        let dhtml = '<a href="index.html">Todo</a>';
        data.categorias.forEach(c => {
            const thumb = c.URL_Imagen ? '<img class="nav-thumb" src="' + c.URL_Imagen + '" onerror="this.style.display=\'none\'">' : '';
            nav.innerHTML += '<a href="colecciones.html?categoria_id=' + c.ID + '">' + thumb + c.Nombre + '</a>';
            dhtml += '<a href="colecciones.html?categoria_id=' + c.ID + '">' + c.Nombre + '</a>';
        });
        if (drawerNav) drawerNav.innerHTML = dhtml;
        const footerCat = document.getElementById('footer-categorias');
        if (footerCat) {
            data.categorias.forEach(c => {
                footerCat.innerHTML += '<a href="colecciones.html?categoria_id=' + c.ID + '">' + c.Nombre + '</a>';
            });
        }
    } else {
        fetch('data.json').then(r => r.ok && r.json()).then(data => {
            if (!data || !data.categorias) return;
            setCachedData(data);
            nav.innerHTML = '<a href="index.html">Todo</a>';
            let dhtml = '<a href="index.html">Todo</a>';
            data.categorias.forEach(c => {
                const thumb = c.URL_Imagen ? '<img class="nav-thumb" src="' + c.URL_Imagen + '" onerror="this.style.display=\'none\'">' : '';
                nav.innerHTML += '<a href="colecciones.html?categoria_id=' + c.ID + '">' + thumb + c.Nombre + '</a>';
                dhtml += '<a href="colecciones.html?categoria_id=' + c.ID + '">' + c.Nombre + '</a>';
            });
            if (drawerNav) drawerNav.innerHTML = dhtml;
            const footerCat = document.getElementById('footer-categorias');
            if (footerCat) {
                data.categorias.forEach(c => {
                    footerCat.innerHTML += '<a href="colecciones.html?categoria_id=' + c.ID + '">' + c.Nombre + '</a>';
                });
            }
        }).catch(() => {});
    }
}

document.addEventListener('DOMContentLoaded', () => {
    cargarProducto();
    cargarNav();
    actualizarContadorCarrito();
    document.getElementById('hamburger-btn')?.addEventListener('click', toggleDrawer);
    document.getElementById('drawer-overlay')?.addEventListener('click', closeDrawer);
    document.getElementById('drawer-close')?.addEventListener('click', closeDrawer);

    document.querySelector('.search-icon')?.addEventListener('click', e => {
        if (window.matchMedia('(max-width: 768px)').matches) {
            e.preventDefault();
            toggleSearchMobile();
        }
    });
});
