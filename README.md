# Asistente de documentos con IA

#Descripción del proyecto
La aplicación fue diseñada como propuesta de proyecto para una empresa de aditivos con certificación FSSC 22000.
El objetivo del proyecto es cargar los procedimientos del Sistema de Gestión de Calidad para tener disponible para consulta información para capacitaciones, revisión de documentos para envio de cuestionarios a clientes, etc.

Así mismo, el programa está diseñado para responder únicamente preguntas relacionadas a los documentos subidos, y especificar en qué documento y párrafos del documento se encuentra la información.

#Tecnologías empleadas
Para la implementación del modelo RAG capaz de realizar el embedding de los documentos y responder las preguntas, se utilizó Langchain.
Como LLM se utilizó la API de Groq.
La implementación y despliegue de la aplicación se realizó con Streamlit.


## Requisitos

- Python 3.10+
- Una API key de Groq

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

#¿Qué preguntas se le pueden realizar? ¿Qué respuestas se pueden esperar del programa?
El programa está diseñado para responder únicamente preguntas relacionadas a los documentos subidos, por ejemplo, con el procedimiento de producción adjunto, puede responder las siguientes preguntas:
- ¿Cual es la primera y segunda etapa dentro del procedimiento de produccion?
- R: Según el procedimiento de producción, la primera etapa es la "Preparación y Pesaje de Materias Primas" (1.1) y la segunda etapa no se especifica explícitamente en el texto proporcionado. Sin embargo, se puede inferir que la segunda etapa es el "Tamizado" (3.1) ya que se menciona como una etapa del proceso de producción en la sección "Descripción del Proceso".

- ¿Cuales son todas las etapas del procedimiento?
- R. Según el procedimiento POE-PROD-001, las etapas del procedimiento son:

Preparación
Tamizado
Mezclado
Dosificación
Empaquetado
Detección de metales
Además, en el Procedimiento de Producción: Sistema HACCP, se describen las siguientes etapas:

Tamizado (Filtro de Seguridad)
Tamizado de Materias Primas: PPO / Control de Peligros Físicos
Mezclado e Homogeneización: Punto de Control (Calidad Funcional)
Es importante destacar que estas etapas pueden variar dependiendo del contexto y la especificación del producto.

- ¿Que documentos están relacionados al procedimiento de producción?
- R. Según el contexto proporcionado, los documentos relacionados al procedimiento de producción son:

Procedimiento de Producción: Sistema HACCP
Procedimiento de Producción y Mezclado de Aditivos en Polvo para Salmueras Cárnicas (Código: POE-PROD-001, Versión: 01)
Estos documentos establecen las actividades y controles necesarios para la producción de aditivos en polvo destinados a la formulación de salmueras de inyección cárnica, garantizando la calidad funcional del producto y la inocuidad alimentaria conforme al plan HACCP.
