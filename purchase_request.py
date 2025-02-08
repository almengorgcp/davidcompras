from flask import Flask, render_template, request, send_file
import csv
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

app = Flask(__name__)

ARCHIVO_CSV = "solicitudes_compras.csv"
CAMPOS = ["Departamento", "Fecha de Solicitud", "Cargo", "Nombre del Responsable", "Finalidad"]

DEPARTAMENTOS = [
    "Asesoría legal", "Bienes patrimoniales", "Bienestar animal", "Concejo municipal",
    "Departamento de Almacén", "Departamento de Auditoria", "Departamento de Compras",
    "Departamento de Deportes", "Departamento de Mantenimientos", "Departamento de Transporte",
    "Descentralización", "Dirección administrativa", "Dirección de Ordenamiento Territorial",
    "Educación y Cultura", "Gestión ambiental", "Ingeniería municipal", "Justicia comunitaria",
    "Planificación financiera", "Recursos humanos", "Relaciones públicas", "Secretaría general",
    "Seguridad ciudadana", "Tesorería", "Vice alcaldía"
]

def guardar_solicitud(datos, articulos):
    """ Guarda los datos en un archivo CSV """
    escribir_encabezado = not os.path.exists(ARCHIVO_CSV)
    
    with open(ARCHIVO_CSV, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        if escribir_encabezado:
            writer.writerow(CAMPOS + ["Artículos"])
        
        articulos_str = "; ".join([f"{a} ({c})" for a, c in articulos])
        writer.writerow(list(datos.values()) + [articulos_str])

def generar_pdf(datos, articulos):
    """ Genera un PDF con logo, encabezado oficial y espaciado correcto """
    archivo_pdf = "solicitud_compra.pdf"
    doc = SimpleDocTemplate(
        archivo_pdf,
        pagesize=letter,
        leftMargin=1.18 * inch,  # 3 cm
        rightMargin=1.18 * inch,  # 3 cm
        topMargin=0.98 * inch,  # 2.5 cm
        bottomMargin=0.98 * inch  # 2.5 cm
    )
    elements = []
    styles = getSampleStyleSheet()

    # ✅ **Definir estilos personalizados**
    style_header_centered = ParagraphStyle(
        "header_centered",
        parent=styles["Normal"],
        fontSize=11,
        leading=12.65,  # Espaciado 1.15
        alignment=TA_CENTER)
    style_body_justified = ParagraphStyle(
        "body_justified",
        parent=styles["Normal"],
        fontSize=11,
        leading=12.65,  # Espaciado 1.15
        alignment=TA_JUSTIFY
    )
    # ✅ **Nuevo estilo para el texto con espaciado 1.5**
    style_body_justified_1_5 = ParagraphStyle(
        "body_justified_1_5",
        parent=styles["Normal"],
        fontSize=11,
        leading=18,  # Espaciado 1.5
        alignment=TA_JUSTIFY
    )

    # ✅ **Agregar Logo y Municipio al Centro**
    logo_path = "imagenes/alcaldia.png"
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=60, height=60)  # Ajustado para que no sea tan grande
        elements.append(logo)

    # ✅ **Texto centrado debajo del logo**
    elements.append(Paragraph("<b>MUNICIPIO DE DAVID</b>", style_header_centered))
    elements.append(Paragraph(f"<b>{datos['Departamento'].upper()}</b>", style_header_centered))

    # Espaciado después del encabezado
    elements.append(Spacer(1, 15))

    # ✅ **Encabezado Justificado con espaciado 1.0**
    header_text = """<b>Honorable</b><br/>
    <b>Joaquín De León</b><br/>
    <b>Alcalde de David</b><br/>
    <b>E. S. D</b>"""
    elements.append(Paragraph(header_text, style_body_justified))

    # ✅ **Espaciado mínimo entre encabezado y el cuerpo**
    elements.append(Spacer(1, 10))

    # ✅ **Texto con espaciado 1.5**
    body_text_1 = "Estimado Honorable,"
    body_text_2 = "Por medio de la presente, el departamento de <b>{}</b> solicita la adquisición de los siguientes bienes o servicios:".format(datos["Departamento"])

    # Agregar el primer párrafo con espaciado 1.5
    elements.append(Paragraph(body_text_1, style_body_justified_1_5))  # Usa estilo con espaciado 1.5
    elements.append(Spacer(1, 10))  # Agrega un espacio extra

    # Agregar el segundo párrafo después del espaciado
    elements.append(Paragraph(body_text_2, style_body_justified_1_5))
    elements.append(Spacer(1, 15))

    # ✅ **Tabla de Artículos alineada con los márgenes**
    tabla_data = [["Artículo", "Cantidad"]]
    tabla_data.extend(articulos)

    table_width = letter[0] - (2 * 1.18 * inch)  # Ajustado para respetar los márgenes
    tabla = Table(tabla_data, colWidths=[table_width * 0.75, table_width * 0.25])  # 75% para Artículo, 25% para Cantidad
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007d9d")),  # Color azul en encabezado
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),  # Texto blanco en encabezado
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),  # Encabezado centrado
        ("ALIGN", (0, 1), (0, -1), "LEFT"),  # Artículos alineados a la izquierda
        ("ALIGN", (1, 1), (1, -1), "CENTER"),  # Cantidad alineada al centro
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),  # Fuente uniforme en la tabla
        ("FONTSIZE", (0, 0), (-1, -1), 11),  # Tamaño de fuente uniforme
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),  # Bordes en la tabla
    ]))
    elements.append(tabla)

    elements.append(Spacer(1, 15))

    # ✅ **Finalidad Justificada**
    elements.append(Paragraph("<b>Finalidad de la compra</b>", style_body_justified_1_5))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(datos["Finalidad"], style_body_justified_1_5))

    elements.append(Spacer(1, 10))

    # ✅ **Mensaje Final Justificado**
    mensaje_final = """Agradecemos de antemano su gestión para la pronta atención de esta solicitud. Quedamos atentos a cualquier consulta o requerimiento adicional."""
    elements.append(Paragraph(mensaje_final, style_body_justified_1_5))

    elements.append(Spacer(1, 20))

    # ✅ **Firma Justificada**
    firma_texto = """<b>Atentamente,</b><br/><br/>
    <b>Firma</b><br/><br/><br/><br/>
    <b>{}</b><br/>
    {}<br/>
    <i>{}</i>
    """.format(datos["Nombre del Responsable"], datos["Cargo"], datos["Departamento"])

    elements.append(Paragraph(firma_texto, style_body_justified))

    # Generar el PDF
    doc.build(elements)
    return archivo_pdf


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  
        datos = {campo: request.form[campo] for campo in CAMPOS}
        articulos = list(zip(request.form.getlist("articulo[]"), request.form.getlist("cantidad[]")))

        guardar_solicitud(datos, articulos)
        archivo_pdf = generar_pdf(datos, articulos)

        return send_file(
            archivo_pdf,
            as_attachment=True,
            mimetype="application/pdf"
        )

    return render_template('formulario.html', departamentos=DEPARTAMENTOS)

if __name__ == "__main__":
    app.run(debug=True)
