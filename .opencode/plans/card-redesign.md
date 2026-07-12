# Plan: Rediseño de Cards + Admin editable

## Objetivo
Rediseñar las collection-card (series/colecciones) para que coincidan con el spec visual, y agregar campos editables (Etiqueta, CTA) en el admin.

---

## 1. index.html

### 1.1 Agregar fuente Press Start 2P
**Localización:** Bloque <head>, línea 17-20, donde se carga Poppins.

**Cambio:** Agregar &family=Press+Start+2P al href de Google Fonts:
`html
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&amp;family=Press+Start+2P&amp;display=swap" rel="stylesheet">
`

### 1.2 Actualizar CSS de .collection-card
**Localización:** Overwrite de las reglas actuales (~líneas 362-418).

**Nuevo CSS (reemplazar reglas existentes de .collection-card, .collection-overlay, .collection-card:hover):**
`css
.collection-card {
    position: relative;
    overflow: hidden;
    aspect-ratio: 2/3;
    border-radius: 24px;
    border: 1px solid var(--border);
    background: var(--surface);
    transition: var(--transition);
    cursor: pointer;
    display: block;
}

.collection-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: var(--transition);
}

.collection-overlay {
    position: absolute;
    inset: 0;
    z-index: 2;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 30px;
    background: linear-gradient(to top, rgba(0,0,0,.92), transparent);
}

.collection-overlay .card-label {
    font-family: 'Press Start 2P', monospace;
    font-size: .6rem;
    color: #38bdf8;
    margin-bottom: 12px;
    letter-spacing: .5px;
}

.collection-overlay h3 {
    font-size: 2rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 10px;
    line-height: 1.2;
}

.collection-overlay p {
    color: #d6d6d6;
    line-height: 1.7;
    font-size: .9rem;
    margin-bottom: 20px;
}

.collection-overlay .card-cta {
    color: #fff;
    font-weight: 700;
    font-size: .95rem;
    transition: var(--transition);
}

.collection-card:hover {
    transform: translateY(-10px);
    border-color: #38bdf8;
    box-shadow: 0 20px 45px rgba(56, 189, 248, .18);
}

.collection-card:hover img {
    transform: scale(1.08);
}

.collection-card:hover .card-cta {
    margin-left: 8px;
}
`

### 1.3 Actualizar enderSeries() JS (~línea 886)
Cambiar el HTML generado por cada card:

**Nuevo código:**
`js
list.forEach(s => {
    const count = allProductos.filter(p => p.Serie_ID === s.ID).length;
    const label = s.Etiqueta || (count + ' diseños');
    const cta = s.CTA_Texto || 'Explorar →';
    seriesGrid.innerHTML +=
        '<div onclick="openSerie(' + s.ID + ')" class="collection-card">' +
            '<img src="' + (s.URL_Imagen || 'https://placehold.co/600x800/1a1a2e/38bdf8?text=' + s.Nombre) + '" onerror="this.src=\'https://placehold.co/600x800/1a1a2e/38bdf8?text=' + s.Nombre + '\'" alt="' + s.Nombre + '">' +
            '<div class="collection-overlay">' +
                '<span class="card-label">' + label + '</span>' +
                '<h3>' + s.Nombre + '</h3>' +
                '<p>' + (s.Descripcion || '') + '</p>' +
                '<span class="card-cta">' + cta + '</span>' +
            '</div>' +
        '</div>';
});
`

---

## 2. colecciones.html

### 2.1 Agregar fuente Press Start 2P
Mismo cambio que index.html (agregar &family=Press+Start+2P al href).

### 2.2 CSS: misma actualización que index.html 1.2
Reemplazar reglas existentes de .collection-card, .collection-overlay, .collection-card:hover.

### 2.3 Actualizar render JS (~línea 221)
Mismo cambio que index.html 1.3:

`js
filtered.forEach(s => {
    const count = allProductos.filter(p => p.Serie_ID === s.ID).length;
    const label = s.Etiqueta || (count + ' diseños');
    const cta = s.CTA_Texto || 'Explorar →';
    grid.innerHTML +=
        '<a href="productos.html?serie_id=' + s.ID + '" class="collection-card">' +
            '<img src="' + (s.URL_Imagen || 'https://placehold.co/600x800/1a1a2e/38bdf8?text=' + s.Nombre) + '" onerror="this.src=\'https://placehold.co/600x800/1a1a2e/38bdf8?text=' + s.Nombre + '\'" alt="' + s.Nombre + '">' +
            '<div class="collection-overlay">' +
                '<span class="card-label">' + label + '</span>' +
                '<h3>' + s.Nombre + '</h3>' +
                '<p>' + (s.Descripcion || '') + '</p>' +
                '<span class="card-cta">' + cta + '</span>' +
            '</div>' +
        '</a>';
});
`

---

## 3. admin.html

### 3.1 Agregar campos al modal de colección
**Localización:** Después del campo "URL de Imagen" (~línea 759), antes del select "Categoría".

**Agregar:**
`html
<label>Etiqueta de card</label>
<input type="text" id="col-etiqueta" placeholder="Ej. 8 diseños, Nueva colección...">
<label>Texto CTA</label>
<input type="text" id="col-cta" placeholder="Ej. Explorar →">
`

### 3.2 Actualizar llamado a editColeccion en renderColecciones (~línea 946)
Cambiar el onclick a:
`js
'<button class="btn-edit" onclick="editColeccion(' + s.ID + ',\'' + s.Nombre.replace(/'/g, "\\'") + '\',\'' + (s.Descripcion || '').replace(/'/g, "\\'") + '\',\'' + (s.URL_Imagen || '').replace(/'/g, "\\'") + '\',\'' + (s.Etiqueta || '').replace(/'/g, "\\'") + '\',\'' + (s.CTA_Texto || '').replace(/'/g, "\\'") + '\',' + s.Categoria_ID + ')"><i class="fas fa-pen"></i></button>'
`

### 3.3 Actualizar función editColeccion (~línea 986)
`js
function editColeccion(id, nombre, desc, url, etiqueta, cta, cat_id) {
    document.getElementById('col-id').value = id;
    document.getElementById('col-nombre').value = nombre;
    document.getElementById('col-desc').value = desc;
    document.getElementById('col-url').value = url;
    document.getElementById('col-etiqueta').value = etiqueta;
    document.getElementById('col-cta').value = cta;
    populateCatSelect('col-cat', cat_id);
    document.getElementById('modal-col-title').textContent = 'Editar Colección';
    openModal('coleccion');
}
`

### 3.4 Actualizar saveColeccion (~línea 961)
Incluir etiqueta y cta_texto en el body:
`js
body: JSON.stringify({
    nombre,
    descripcion,
    url_imagen,
    etiqueta: document.getElementById('col-etiqueta').value,
    cta_texto: document.getElementById('col-cta').value,
    categoria_id
})
`

### 3.5 Actualizar show handler del modal colección (~línea 1083)
Agregar reset:
`js
document.getElementById('col-etiqueta').value = '';
document.getElementById('col-cta').value = '';
`

---

## Notas
- Los campos Etiqueta y CTA_Texto no existen aún en la DB. El frontend usa fallbacks (||).
- Cuando se agreguen las columnas a la DB, actualizar backend POST/PUT de series para aceptar etiqueta y cta_texto.
