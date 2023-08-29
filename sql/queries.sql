CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY,
            familia VARCHAR(255),
            proveedor VARCHAR(255),
            nombre VARCHAR(255),
            precio_neto FLOAT,
            precio_compra FLOAT,
            unidad_compra VARCHAR(50),
            formato FLOAT NOT NULL DEFAULT 0.0,
            peso_bruto FLOAT NOT NULL DEFAULT 0.0,
            merma FLOAT NOT NULL DEFAULT 0.0,
            peso_neto FLOAT, 
            factor_merma FLOAT DEFAULT 0.0,
            existencias FLOAT DEFAULT 0.0
        );

CREATE TABLE IF NOT EXISTS platos (
        id INTEGER PRIMARY KEY,
        zona VARCHAR(255) DEFAULT '',
        categoria VARCHAR(255),
        nombre_plato VARCHAR(255),
        Fecha DATE,
        porcion_grs REAL NOT NULL DEFAULT 0.0,
        numero_porciones REAL NOT NULL DEFAULT 0.0,
        tiempo_prep_mins REAL NOT NULL DEFAULT 0.0,
        tiempo_coccion_mins REAL NOT NULL DEFAULT 0.0,
        temp_serv_c REAL NOT NULL DEFAULT 0.0,
        precio_venta REAL NOT NULL DEFAULT 0.0,
        impuesto REAL,
        precio_neto REAL,
        costo_receta FLOAT,
        costo_receta_perc REAL,
        beneficio REAL,
        elaboracion VARCHAR(1200) NOT NULL DEFAULT '',
        presentacion VARCHAR(500) NOT NULL DEFAULT '',
        equipo_elaboracion VARCHAR(500) NOT NULL DEFAULT '',
        gluten_alg BITSTRING,
        crustaceo_alg BITSTRING,
        huevo_alg BITSTRING,
        pescado_alg BITSTRING,
        cacahuetes_alg BITSTRING,
        lacteos_alg BITSTRING,
        apio_alg BITSTRING,
        mostaza_alg BITSTRING,
        sulfitos_alg BITSTRING,
        sesamo_alg BITSTRING,
        moluscos_alg BITSTRING,
        soja_alg BITSTRING,
        frutos_secos_alg BITSTRING,
        altramuz_alg BITSTRING,
        foto_plato BLOB DEFAULT NULL,
        plato_activo BITSTRING
        );
        
CREATE TABLE IF NOT EXISTS plato_ingredientes (
        id_plato INTEGER,
        id_inventario INTEGER,
        PRIMARY KEY (id_plato, id_inventario),
        FOREIGN KEY (id_plato) REFERENCES platos (id),
        FOREIGN KEY (id_inventario) REFERENCES inventario (id)
        );
        
CREATE TABLE IF NOT EXISTS ingenieria_menu (
        id_plato INTEGER,
        indice_popularidad REAL NOT NULL DEFAULT 0.0,
        coste_producto_porcentage REAL DEFAULT 0.0,
        margen_contribucion REAL NOT NULL DEFAULT 0.0,
        total_coste_producto REAL NOT NULL DEFAULT 0.0,
        total_venta_producto REAL NOT NULL DEFAULT 0.0,
        total_margen REAL NOT NULL DEFAULT 0.0,
        rentabilidad VARCHAR(16) DEFAULT NULL,
        popularidad VARCHAR(16) DEFAULT NULL,
        clasificacion VARCHAR(16) DEFAULT NULL,
        PRIMARY KEY (id_plato),
        FOREIGN KEY (id_plato) REFERENCES platos (id)
        );
        
CREATE TABLE IF NOT EXISTS ventas_productos (
        Fecha VARCHAR(10),
        id_plato INTEGER,
        nombre_plato VARCHAR(50),
        unidades_vendidas REAL NOT NULL DEFAULT 0.0,
        PRIMARY KEY (id_plato),
        FOREIGN KEY (id_plato) REFERENCES platos (id)
    );




