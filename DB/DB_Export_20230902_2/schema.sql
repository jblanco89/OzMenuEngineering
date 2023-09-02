


CREATE TABLE inventario(id INTEGER PRIMARY KEY, familia VARCHAR, proveedor VARCHAR, nombre VARCHAR, precio_neto FLOAT NOT NULL DEFAULT(1.0), precio_compra FLOAT DEFAULT(1.0), unidad_compra VARCHAR, formato FLOAT NOT NULL DEFAULT(1.0), peso_bruto FLOAT NOT NULL DEFAULT(1.0), merma FLOAT NOT NULL DEFAULT(1.0), peso_neto FLOAT NOT NULL DEFAULT(1.0), factor_merma FLOAT DEFAULT(1.0), existencias FLOAT DEFAULT(1.0));
CREATE TABLE platos(id INTEGER PRIMARY KEY, zona VARCHAR DEFAULT(''), categoria VARCHAR, nombre_plato VARCHAR, "Fecha" DATE, porcion_grs FLOAT NOT NULL DEFAULT(0.0), numero_porciones FLOAT NOT NULL DEFAULT(0.0), tiempo_prep_mins FLOAT NOT NULL DEFAULT(0.0), tiempo_coccion_mins FLOAT NOT NULL DEFAULT(0.0), temp_serv_c FLOAT NOT NULL DEFAULT(0.0), precio_venta FLOAT NOT NULL DEFAULT(0.0), impuesto FLOAT, precio_neto FLOAT, costo_receta FLOAT, costo_receta_perc FLOAT, beneficio FLOAT, elaboracion VARCHAR NOT NULL DEFAULT(''), presentacion VARCHAR NOT NULL DEFAULT(''), equipo_elaboracion VARCHAR NOT NULL DEFAULT(''), gluten_alg BIT, crustaceo_alg BIT, huevo_alg BIT, pescado_alg BIT, cacahuetes_alg BIT, lacteos_alg BIT, apio_alg BIT, mostaza_alg BIT, sulfitos_alg BIT, sesamo_alg BIT, moluscos_alg BIT, soja_alg BIT, frutos_secos_alg BIT, altramuz_alg BIT, foto_plato BLOB DEFAULT(NULL), plato_activo BIT);
CREATE TABLE alergenos(id_plato INTEGER, alergeno VARCHAR, presencia BOOLEAN, FOREIGN KEY (id_plato) REFERENCES platos(id));
CREATE TABLE plato_ingredientes(id_plato INTEGER, id_inventario INTEGER, porcion_ing_grs FLOAT DEFAULT(0.0), PRIMARY KEY(id_plato, id_inventario), FOREIGN KEY (id_plato) REFERENCES platos(id), FOREIGN KEY (id_inventario) REFERENCES inventario(id));
CREATE TABLE ingenieria_menu(id_plato INTEGER, indice_popularidad FLOAT NOT NULL DEFAULT(0.0), coste_producto_porcentage FLOAT DEFAULT(0.0), margen_contribucion FLOAT NOT NULL DEFAULT(0.0), total_coste_producto FLOAT NOT NULL DEFAULT(0.0), total_venta_producto FLOAT NOT NULL DEFAULT(0.0), total_margen FLOAT NOT NULL DEFAULT(0.0), rentabilidad VARCHAR DEFAULT(NULL), popularidad VARCHAR DEFAULT(NULL), clasificacion VARCHAR DEFAULT(NULL), PRIMARY KEY(id_plato), FOREIGN KEY (id_plato) REFERENCES platos(id));
CREATE TABLE ventas_productos("Fecha" VARCHAR, id_plato INTEGER, nombre_plato VARCHAR, unidades_vendidas FLOAT NOT NULL DEFAULT(0.0), FOREIGN KEY (id_plato) REFERENCES platos(id));




