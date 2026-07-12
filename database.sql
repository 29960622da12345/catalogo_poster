CREATE DATABASE IF NOT EXISTS squirrel_db;
USE squirrel_db;

-- Crear un usuario nativo para la API de Python y evitar el error auth_gssapi_client
CREATE USER IF NOT EXISTS 'squirrel_user'@'localhost' IDENTIFIED BY 'squirrel123';
GRANT ALL PRIVILEGES ON squirrel_db.* TO 'squirrel_user'@'localhost';
FLUSH PRIVILEGES;


CREATE TABLE IF NOT EXISTS Admins (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Usuario VARCHAR(50) NOT NULL UNIQUE,
    Contrasena VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Categorias (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    URL_Imagen TEXT
);

CREATE TABLE IF NOT EXISTS Series (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(150) NOT NULL,
    Descripcion TEXT,
    URL_Imagen TEXT,
    Categoria_ID INT,
    FOREIGN KEY (Categoria_ID) REFERENCES Categorias(ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Imagenes_Productos (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(150) NOT NULL,
    URL_Imagen TEXT NOT NULL,
    Serie_ID INT,
    Categoria_ID INT,
    Precio VARCHAR(50),
    FOREIGN KEY (Serie_ID) REFERENCES Series(ID) ON DELETE SET NULL,
    FOREIGN KEY (Categoria_ID) REFERENCES Categorias(ID) ON DELETE SET NULL
);

-- Migraciones para tablas existentes:
-- ALTER TABLE Imagenes_Productos ADD COLUMN Categoria_ID INT AFTER Serie_ID,
-- ADD FOREIGN KEY (Categoria_ID) REFERENCES Categorias(ID) ON DELETE SET NULL;
-- ALTER TABLE Imagenes_Productos ADD COLUMN Precio VARCHAR(50) AFTER Categoria_ID;

-- Insertar administrador de prueba
INSERT INTO Admins (Usuario, Contrasena) VALUES ('admin', 'admin123')
ON DUPLICATE KEY UPDATE Usuario=Usuario;

-- Insertar algunas categorías por defecto
INSERT INTO Categorias (Nombre, URL_Imagen) VALUES 
('Anime', 'https://placehold.co/400x600/1a1a2e/ffffff?text=Anime'),
('Videojuegos', 'https://placehold.co/400x600/16213e/ffffff?text=Videojuegos'),
('Deportes', 'https://placehold.co/400x600/0f3460/ffffff?text=Deportes');
