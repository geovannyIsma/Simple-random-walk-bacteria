import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSpinBox, QPushButton, QVBoxLayout, QFormLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

def solicitar_datos():
    class VentanaEntrada(QWidget):
        def __init__(self):
            super().__init__()
            self.initUI()
            self.resultado = None

        def initUI(self):
            self.setWindowTitle('Configuración inicial')
            self.setGeometry(100, 100, 500, 300)
            self.setFixedSize(500, 300)
            self.setWindowIcon(QIcon('path/to/icon.png'))  # Añade la ruta de tu icono aquí
            self.centrar()

            layout = QVBoxLayout()

            layout_formulario = QFormLayout()
            self.etiqueta_ciclos = QLabel('Número de ciclos:')
            self.entrada_ciclos = QSpinBox()
            self.entrada_ciclos.setRange(1, 10000)
            self.entrada_ciclos.setKeyboardTracking(False)
            layout_formulario.addRow(self.etiqueta_ciclos, self.entrada_ciclos)

            self.etiqueta_vida = QLabel('Vida inicial de la bacteria:')
            self.entrada_vida = QSpinBox()
            self.entrada_vida.setRange(1, 10000)
            self.entrada_vida.setKeyboardTracking(False)
            layout_formulario.addRow(self.etiqueta_vida, self.entrada_vida)

            self.etiqueta_comida = QLabel('Número de comidas:')
            self.entrada_comida = QSpinBox()
            self.entrada_comida.setRange(1, 10000)
            self.entrada_comida.setKeyboardTracking(False)
            layout_formulario.addRow(self.etiqueta_comida, self.entrada_comida)

            self.etiqueta_particulas = QLabel('Número de partículas:')
            self.entrada_particulas = QSpinBox()
            self.entrada_particulas.setRange(1, 10000)
            self.entrada_particulas.setKeyboardTracking(False)
            layout_formulario.addRow(self.etiqueta_particulas, self.entrada_particulas)

            layout.addLayout(layout_formulario)

            self.boton_enviar = QPushButton('Iniciar Simulación')
            self.boton_enviar.setFixedHeight(40)
            self.boton_enviar.setFixedWidth(200)
            self.boton_enviar.clicked.connect(self.al_enviar)
            layout.addWidget(self.boton_enviar, alignment=Qt.AlignCenter)

            self.setLayout(layout)
            self.aplicar_estilos()

        def centrar(self):
            qr = self.frameGeometry()
            cp = QApplication.desktop().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())

        def aplicar_estilos(self):
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e1e2e;
                    color: #c0c0c0;
                    font-family: 'Roboto', sans-serif;
                    font-size: 16px;
                }
                QLabel {
                    margin-bottom: 10px;
                }
                QSpinBox {
                    background-color: #2e2e3e;
                    border: 1px solid #4e4e6e;
                    padding: 5px;
                    margin-bottom: 15px;
                    color: #c0c0c0;
                }
                QPushButton {
                    background-color: #3e3e5e;
                    border: none;
                    padding: 10px;
                    color: #c0c0c0;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5e5e7e;
                }
            """)

        def al_enviar(self):
            try:
                num_ciclos = self.entrada_ciclos.value()
                vida_inicial = self.entrada_vida.value()
                num_comida = self.entrada_comida.value()
                num_particulas = self.entrada_particulas.value()
                if num_ciclos <= 0 or vida_inicial <= 0 or num_comida <= 0 or num_particulas <= 0:
                    raise ValueError
                self.resultado = (num_ciclos, vida_inicial, num_comida, num_particulas)
                self.close()
            except ValueError:
                QMessageBox.critical(self, "Error", "Por favor, ingrese un número entero válido.")
                self.entrada_ciclos.clear()
                self.entrada_vida.clear()
                self.entrada_comida.clear()
                self.entrada_particulas.clear()

    app = QApplication(sys.argv)
    ventana = VentanaEntrada()
    ventana.show()
    app.exec_()
    return ventana.resultado
