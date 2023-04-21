from io import BytesIO
create_inventory_table = '''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY,
            nombre VARCHAR(255),
            familia VARCHAR(255),
            proveedor VARCHAR(255),
            precio_neto FLOAT,
            precio_compra FLOAT,
            unidad_compra VARCHAR(50),
            formato FLOAT,
            peso_bruto FLOAT,
            merma FLOAT,
            peso_neto FLOAT, 
            factor_merma FLOAT,
            existencias FLOAT
        );
        '''
create_ingredients_table = '''
        CREATE TABLE IF NOT EXISTS ingredientes (
            id INTEGER PRIMARY KEY,
            id_inventario INTEGER,
            nombre VARCHAR(255) DEFAULT '',
            cantidad REAL NOT NULL DEFAULT 0.0,
            unidad_real VARCHAR(255),
            precio_compra DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
            unidad_compra VARCHAR(255) DEFAULT '',
            factor_merma REAL NOT NULL DEFAULT 0.00,
            coste_ingrediente DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
            FOREIGN KEY (id_inventario) REFERENCES inventario (id)
        );
        '''


create_meals_table = '''
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
    '''
# FOREIGN KEY (id_ingrediente) REFERENCES ingredientes (id)
create_meal_ingredient_table = '''
    CREATE TABLE IF NOT EXISTS plato_ingredientes (
    id_ingrediente INTEGER,
    id_plato INTEGER,
    FOREIGN KEY (id_plato) REFERENCES platos (id),
    FOREIGN KEY (id_ingrediente) REFERENCES ingredientes (id)
    );

'''
with open('img/Imagen1.jpg', 'rb') as f:
    image_data = f.read()

img_insert = BytesIO(image_data)

insert_meals_data = f'''
    INSERT OR IGNORE INTO platos 
    (id,
    categoria,
    nombre_plato,
    Fecha,
    porcion_grs,
    numero_porciones,
    precio_venta, 
    costo_receta,
    foto_plato,
    plato_activo
    )
    VALUES (
        1,
        'Principal',
        'Plato Inicial', 
        '2022-08-22',
        150.15,
        1.0, 
        15.99,
        3.50,
        '{img_insert}',
        '1'
        );
'''

insert_ingredients_data = '''
    INSERT OR IGNORE INTO ingredientes 
    (id, 
    nombre, 
    unidad_real, 
    precio_compra, 
    unidad_compra,
    factor_merma
    )
    VALUES (1,'pasta', 'gramos', 2.5, 'Kg', 1000.00),
       (2, 'ground beef', 'gramos', 1.2, 'Kg', 1000.00),
       (3, 'tomato sauce', 'gramos', 2.5, 'Kg', 1000.00),
       (4, 'onions', 'gramos', 0.45, 'Kg', 1000.00);
'''

insert_ingredient_meal_data = '''
    INSERT OR IGNORE INTO plato_ingredientes 
    (id_plato, 
    id_ingrediente,
    )
    VALUES (1, 1), (1, 2), (1, 3), (1, 4);
'''

insert_inventory_data = '''
    INSERT INTO inventario 
    SELECT 
    ID, 
    PRODUCTO, 
    FAMILIA, 
    PROVEEDOR,
    UDNeto, 
    UDCompra, 
    UD, 
    FORMATO, 
    PESOBruto, 
    MERMA,
    (PESOBruto - MERMA) AS PESONeto, 
    FACTORMerma,
    EXISTENCIAS 
    FROM read_csv('C:/Users/javie/Documents/Jami/Jami-Project/Escandallo/MenuEngine/external_csv/inventario_dev.csv', 
    delim=';', header=True, ignore_errors=1,
    columns={
        'ID': 'INTEGER', 
        'PRODUCTO': 'VARCHAR', 
        'FAMILIA': 'VARCHAR', 
        'PROVEEDOR': 'VARCHAR',
        'UDNeto': 'FLOAT',
        'UDCompra': 'FLOAT',
        'UD': 'VARCHAR',
        'FORMATO': 'FLOAT',
        'PESOBruto': 'FLOAT',
        'MERMA': 'FLOAT',
        'FACTORMerma': 'FLOAT',
        'PESONeto': 'FLOAT',
        'EXISTENCIAS': 'FLOAT'
        }
        )
        WHERE NOT EXISTS (SELECT * FROM inventario);
        ''' 