import base64
create_inventory_table = '''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY,
            familia VARCHAR(255),
            proveedor VARCHAR(255),
            nombre VARCHAR(255),
            precio_neto FLOAT NOT NULL DEFAULT 1.0,
            precio_compra FLOAT DEFAULT 1.0,
            unidad_compra VARCHAR(50),
            formato FLOAT NOT NULL DEFAULT 1.0,
            peso_bruto FLOAT NOT NULL DEFAULT 1.0,
            merma FLOAT NOT NULL DEFAULT 1.0,
            peso_neto FLOAT NOT NULL DEFAULT 1.0, 
            factor_merma FLOAT DEFAULT 1.0,
            existencias FLOAT DEFAULT 1.0
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
        foto_plato BLOB DEFAULT NULL,
        plato_activo BITSTRING
        );
    '''

create_allergen_table = ''' CREATE TABLE IF NOT EXISTS alergenos (
        id_plato INTEGER,
        alergeno TEXT PRIMARY KEY,
        presencia BOOLEAN,
        FOREIGN KEY (id_plato) REFERENCES platos (id) ON DELETE CASCADE 
    );
    '''

create_meal_ingredient_table = '''
    CREATE TABLE IF NOT EXISTS plato_ingredientes (
        id_plato INTEGER,
        id_inventario INTEGER,
        porcion_ing_grs FLOAT DEFAULT 0.0,
        PRIMARY KEY (id_plato, id_inventario),
        FOREIGN KEY (id_plato) REFERENCES platos (id) ON DELETE CASCADE,
        FOREIGN KEY (id_inventario) REFERENCES inventario (id) ON DELETE CASCADE
        );

'''

create_menu_engine_table = '''
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
        FOREIGN KEY (id_plato) REFERENCES platos (id) ON DELETE CASCADE
        );
'''

create_sales_table = '''
    CREATE TABLE IF NOT EXISTS ventas_productos (
        Fecha VARCHAR(10),
        id_plato INTEGER,
        nombre_plato VARCHAR(50),
        unidades_vendidas REAL NOT NULL DEFAULT 0.0,
        FOREIGN KEY (id_plato) REFERENCES platos (id) ON DELETE CASCADE
    );

'''

with open('img/Imagen1.jpg', 'rb') as f:
    image_data = f.read()

img_insert = base64.b64encode(image_data).decode('utf-8')

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


insert_ingredient_meal_data = '''
    INSERT OR IGNORE INTO plato_ingredientes 
    (id_plato, 
    id_inventario
    )
    VALUES (1, 100004), (1, 100007), (1, 100048), (1, 100077);
'''

insert_inventory_data = '''
    INSERT OR IGNORE INTO inventario 
    SELECT 
    ID, 
    FAMILIA, 
    PROVEEDOR, 
    PRODUCTO,
    UDNeto, 
    UDCompra, 
    UD, 
    FORMATO, 
    PESOBruto, 
    MERMA,
    (PESOBruto - MERMA) AS PESONeto, 
    FACTORMerma,
    EXISTENCIAS 
    FROM read_csv('external_csv/inventario_dev.csv', 
    delim=';', header=True, ignore_errors=1,
    columns={
        'ID': 'INTEGER', 
        'FAMILIA': 'VARCHAR', 
        'PROVEEDOR': 'VARCHAR', 
        'PRODUCTO': 'VARCHAR',
        'UDNeto': 'FLOAT NOT NULL DEFAULT 1.0',
        'UDCompra': 'FLOAT',
        'UD': 'VARCHAR',
        'FORMATO': 'FLOAT',
        'PESOBruto': 'FLOAT NOT NULL DEFAULT 1.0',
        'MERMA': 'FLOAT NOT NULL DEFAULT 1.0',
        'FACTORMerma': 'FLOAT NOT NULL DEFAULT 1.0',
        'PESONeto': 'FLOAT NOT NULL DEFAULT 1.0',
        'EXISTENCIAS': 'FLOAT NOT NULL DEFAULT 1.0'
        }
        )
        WHERE NOT EXISTS (SELECT * FROM inventario);
        '''


insert_sales_data = '''
    INSERT OR IGNORE INTO ventas_productos (
    Fecha,
    id_plato,
    nombre_plato,
    unidades_vendidas)
    VALUES (
    '2022/03/01',
    1,
    'CEVICHE',
    0.0
    );

'''

insert_menu_engine_value = '''
    INSERT OR IGNORE INTO ingenieria_menu
    (id_plato,
    indice_popularidad,
    coste_producto_porcentage,
    margen_contribucion,
    total_coste_producto,
    total_venta_producto,
    total_margen,
    rentabilidad,
    popularidad,
    clasificacion)
    VALUES
    (1,
    0.5,
    0.5,
    0.0,
    0.0,
    0.0,
    0.0,
    'ALTO',
    'ALTO',
    'ESTRELLA');

'''

cross_platos_ingredientes = '''
    SELECT DISTINCT 
    p.nombre_plato, 
    p.precio_venta, 
    p.porcion_grs, 
    p.costo_receta, 
    i.nombre, 
    i.precio_compra, 
    pli.porcion_ing_grs, 
    p.beneficio 
    FROM platos as p 
    LEFT JOIN plato_ingredientes as pli 
    ON p.id = pli.id_plato 
    LEFT JOIN inventario as i 
    ON pli.id_inventario = i.id 
    WHERE p.id = ? 
    ORDER BY 
    pli.porcion_ing_grs DESC;
'''

correct_inventario_data = '''
    UPDATE inventario 
    SET precio_neto = COALESCE(precio_neto,1), 
    precio_compra = COALESCE(precio_compra,1), 
    peso_bruto = COALESCE(peso_bruto, 1), 
    peso_neto = COALESCE(peso_neto,1), 
    merma = COALESCE(merma,1), 
    factor_merma = COALESCE(merma,1), 
    existencias = COALESCE(existencias,1) 
    WHERE 
    precio_neto = 0 OR precio_neto IS NULL OR 
    precio_compra = 0 OR precio_compra IS NULL OR 
    peso_bruto = 0 OR peso_bruto IS NULL OR 
    peso_neto = 0 OR peso_neto IS NULL OR 
    merma = 0 OR merma IS NULL OR 
    factor_merma = 0 OR factor_merma IS NULL OR 
    existencias = 0 OR existencias IS NULL;

'''