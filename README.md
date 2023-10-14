## ER Schema of Application

 ![architecture](./sql/E-R_Diagram_v3.png)

 ## Ingredients and meal ETL

 ```m
 let
    Origen = Csv.Document(File.Contents("C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\Uploads\meal_list_unique_completed.csv"),[Delimiter=";", Columns=2, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Encabezados promovidos" = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Encabezados promovidos",{{"Codigo", Int64.Type}, {"Nombre", type text}}),
    #"Texto limpio" = Table.TransformColumns(#"Tipo cambiado",{{"Nombre", Text.Clean, type text}}),
    #"Poner En Mayúsculas Cada Palabra" = Table.TransformColumns(#"Texto limpio",{{"Nombre", Text.Proper, type text}}),
    #"Texto recortado" = Table.TransformColumns(#"Poner En Mayúsculas Cada Palabra",{{"Nombre", Text.Trim, type text}})
in
    #"Texto recortado"


let
    Origen = Csv.Document(File.Contents("C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\external_csv\inventario_dev.csv"),[Delimiter=";", Columns=15, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Encabezados promovidos" = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Encabezados promovidos",{{"ID", Int64.Type}, {"FAMILIA", type text}, {"PROVEEDOR", type text}, {"PRODUCTO", type text}, {"UDNeto", Int64.Type}, {"UDCompra", Int64.Type}, {"UD", type text}, {"FORMATO", Int64.Type}, {"PESOBruto", Int64.Type}, {"ENVASE", Int64.Type}, {"PesoAntesEscurrido", Int64.Type}, {"PESONeto", Int64.Type}, {"MERMA", Int64.Type}, {"FACTORMerma", Int64.Type}, {"EXISTENCIAS", Int64.Type}}),
    #"Otras columnas quitadas" = Table.SelectColumns(#"Tipo cambiado",{"ID", "PRODUCTO"}),
    #"Texto limpio" = Table.TransformColumns(#"Otras columnas quitadas",{{"PRODUCTO", Text.Clean, type text}}),
    #"Poner En Mayúsculas Cada Palabra" = Table.TransformColumns(#"Texto limpio",{{"PRODUCTO", Text.Proper, type text}}),
    #"Texto recortado" = Table.TransformColumns(#"Poner En Mayúsculas Cada Palabra",{{"PRODUCTO", Text.Trim, type text}})
in
    #"Texto recortado"

 ```

 ## Some SQL Statements

 ```sql
WITH ventas_summary AS (
        SELECT 
        id_plato,
        nombre_plato,
        SUM(unidades_vendidas) AS unidades_vendidas
        FROM
        ventas_productos
        WHERE Fecha >= ? AND Fecha <= ?
        GROUP BY nombre_plato, id_plato

)
SELECT 
p.nombre_plato, 
v.unidades_vendidas, 
p.costo_receta, 
p.precio_venta, 
(p.costo_receta / p.precio_venta * 100) AS coste_producto_porcentage,
(p.precio_venta - p.costo_receta) AS margen_contribucion,
(v.unidades_vendidas * p.costo_receta) AS total_coste_producto,
(v.unidades_vendidas * p.precio_venta) AS total_venta_producto,
(total_venta_producto - total_coste_producto) AS total_margen,
FROM platos AS p 
INNER JOIN ventas_summary AS v 
ON p.id = v.id_plato


WITH csv_data AS (
    SELECT Codigo_Plato, Codigo_Ingrediente, Porciones
    FROM read_csv_auto('C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\Uploads\insert_meal_ingredients_data.csv', delim=';', header=True, ignore_errors=1)
)

INSERT OR IGNORE INTO plato_ingredientes
(id_plato,
id_inventario,
porcion_ing_grs)
SELECT Codigo_Plato, Codigo_Ingrediente, Porciones
FROM csv_data;


INSERT INTO inventario 
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
    ENVASE,
    PesoAntesEscurrido, 
    MERMA,
    PESONeto, 
    FACTORMerma,
    EXISTENCIAS 
    FROM read_csv('external_csv/inventario_dev.csv', 
    delim=';', header=True,
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
        'ENVASE':'FLOAT NOT NULL DEFAULT 1.0',
        'PesoAntesEscurrido': 'FLOAT NOT NULL DEFAULT 1.0',
        'PESONeto': 'FLOAT NOT NULL DEFAULT 1.0',
        'MERMA': 'FLOAT NOT NULL DEFAULT 1.0',
        'FACTORMerma': 'FLOAT NOT NULL DEFAULT 1.0',
        'EXISTENCIAS': 'FLOAT NOT NULL DEFAULT 1.0'
        }
        )
        WHERE NOT EXISTS (SELECT * FROM inventario);


 ```

 ## VBA Scripts 

 ```vb
 Sub getIngredients()
    Dim wb As Workbook
    Dim sh As Worksheet
    Dim mealWorkbook As Workbook
    Dim mealWorksheet As Worksheet
    Dim mealName As range
    Dim ingredientList As range
    Dim ingredient As range
    Dim portions As range
    Dim extractedMealName As String
    Dim extractedIngredient As String
    Dim extractedPortion As String

    Set wb = ThisWorkbook
    Set sh = wb.Sheets(1)

    Set mealWorkbook = Workbooks.Open("C:\Users\javie\Documents\Jami\Jami-Project\docs\FICHA_PLATO_ESCANDALLO.xlsx")

    For Each mealWorksheet In mealWorkbook.Sheets
        Set mealName = mealWorksheet.range("A4")
        Set ingredientList = mealWorksheet.range("A16:A28")
        Set portions = mealWorksheet.range("B16:B28")

        extractedMealName = mealName.Value
        extractedMealName = WorksheetFunction.Proper(extractedMealName)
        
        For Each ingredient In ingredientList
            If Not IsEmpty(ingredient.Value) Then
                extractedIngredient = ingredient.Value
                Dim emptyRow As Long
                emptyRow = sh.Cells(sh.Rows.Count, 2).End(xlUp).Row + 1
                sh.Cells(emptyRow, 2).Value = extractedMealName
                sh.Cells(emptyRow, 3).Value = extractedIngredient
            End If
        Next ingredient
        For Each portion In portions
            If Not IsEmpty(portion.Value) Then
                extractedPortion = portion.Value
                Dim emptyRow As Long
                emptyRow = sh.Cells(sh.Rows.Count, 5).End(xlUp).Row + 1
                sh.Cells(emptyRow, 5).Value = extractedPortion
            End If
        Next portion
    Next mealWorksheet

    mealWorkbook.Close SaveChanges:=False

    MsgBox "Data extraction completed!", vbInformation
End Sub



 ```