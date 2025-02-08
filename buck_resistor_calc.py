import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,  # 添加这一行
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTextEdit,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
)
from PyQt5.QtCore import Qt


class ResistorCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        # Define calculation methods before initializing UI
        self.calculate_combinations = self.calculate_combinations_method
        self.calculate_voltage = self.calculate_voltage_method
        self.filter_results = self.filter_results_method
        self.toggle_mode = self.toggle_mode_method
        self.initUI()

    def format_resistance(self, value):
        if value >= 1e6:
            return f"{value/1e6:.2f}M".rstrip("0").rstrip(".")
        elif value >= 1e3:
            k_value = value / 1e3
            if k_value >= 100:
                return f"{k_value:.1f}k".rstrip("0").rstrip(".")
            else:
                return f"{k_value:.2f}k".rstrip("0").rstrip(".")
        else:
            return f"{value:.1f}".rstrip("0").rstrip(".")

    def read_resistor_list(self):
        base_values = []
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, "resistor_list.txt"), "r") as f:
            base_values = [float(line.strip()) for line in f.readlines()]

        extended_values = []
        for value in base_values:
            for multiplier in [1, 10, 100, 1000, 10000]:
                extended_values.append(value * multiplier)
        return sorted(extended_values)

    def toggle_mode_method(self):
        is_voltage_mode = self.voltage_mode.isChecked()
        self.vout_input.setEnabled(is_voltage_mode)
        # 删除 self.vfb_input.setEnabled(is_voltage_mode)
        self.error_combo.setEnabled(is_voltage_mode)
        self.calc_voltage_btn.setEnabled(is_voltage_mode)

        self.rfbt_input.setEnabled(not is_voltage_mode)
        self.rfbb_input.setEnabled(not is_voltage_mode)
        self.calc_resistor_btn.setEnabled(not is_voltage_mode)

    def toggle_mode(self):
        is_voltage_mode = self.voltage_mode.isChecked()
        self.vout_input.setEnabled(is_voltage_mode)
        # 删除 self.vfb_input.setEnabled(is_voltage_mode)
        self.error_combo.setEnabled(is_voltage_mode)
        self.calc_voltage_btn.setEnabled(is_voltage_mode)

        self.rfbt_input.setEnabled(not is_voltage_mode)
        self.rfbb_input.setEnabled(not is_voltage_mode)
        self.calc_resistor_btn.setEnabled(not is_voltage_mode)

    def filter_results_method(self):
        if self.voltage_mode.isChecked():
            self.calculate_combinations()
        else:
            self.calculate_voltage()

    def calculate_combinations_method(self):
        try:
            vout = float(self.vout_input.text())
            vfb = float(self.vfb_input.text())
            error_percent = float(self.error_combo.currentText())

            resistor_list = self.read_resistor_list()
            results = []

            for rfbb in resistor_list:
                for rfbt in resistor_list:
                    actual_vout = vfb * (1 + rfbt / rfbb)
                    error = ((actual_vout - vout) / vout) * 100

                    if abs(error) <= error_percent:
                        if not self.filter_check.isChecked() or (
                            rfbt >= 1000 and rfbb >= 1000
                        ):
                            results.append((rfbt, rfbb, error))

            # 按照 Rfbt 从小到大排序
            results.sort(key=lambda x: x[0])

            self.result_text.clear()

            for rfbt, rfbb, error in results:
                actual_vout = vfb * (1 + rfbt / rfbb)
                self.result_text.append(
                    f"Rfbt(Vout) = {self.format_resistance(rfbt)}, "
                    f"Rfbb(Gnd) = {self.format_resistance(rfbb)}, "
                    f"Err = {'+' if error > 0 else ''}{error:.1f}%, "
                    f"Vout = {actual_vout:.3f}V"
                )

        except ValueError:
            self.result_text.setText("Please enter valid numbers")

    def calculate_voltage_method(self):
        try:
            rfbt = float(self.rfbt_input.text()) * 1000
            rfbb = float(self.rfbb_input.text()) * 1000
            vfb = float(self.vfb_input.text())
            actual_vout = vfb * (1 + rfbt / rfbb)

            self.result_text.clear()
            self.result_text.append(
                f"Rfbt = {self.format_resistance(rfbt)}, "
                f"Rfbb = {self.format_resistance(rfbb)}, "
                f"Vout = {actual_vout:.3f}V"
            )
        except ValueError:
            self.result_text.setText("Please enter valid numbers")

    def initUI(self):
        self.setWindowTitle("buck_resistor_calc")
        self.setGeometry(300, 300, 800, 600)
        self.setFixedWidth(500)  # fix size

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 模式选择
        mode_layout = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        self.voltage_mode = QRadioButton("Calc Resistor")
        self.resistor_mode = QRadioButton("Calc Voltage")
        self.voltage_mode.setChecked(True)
        self.mode_group.addButton(self.voltage_mode)
        self.mode_group.addButton(self.resistor_mode)
        mode_layout.addWidget(self.voltage_mode)
        mode_layout.addWidget(self.resistor_mode)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # 输入区域
        input_layout = QVBoxLayout()

        input_grid = QGridLayout()

        # vol
        self.vout_label = QLabel("Vout(V):")
        self.vout_input = QLineEdit()
        self.vout_input.setFixedWidth(80)
        self.vout_input.setText("12")
        self.vfb_label = QLabel("Vfb(V):")
        self.vfb_input = QLineEdit()
        self.vfb_input.setFixedWidth(80)
        self.vfb_input.setText("0.85")
        self.calc_voltage_btn = QPushButton("Result")
        self.calc_voltage_btn.setFixedWidth(100)

        # res
        self.rfbt_label = QLabel("Rfbt(kΩ):")
        self.rfbt_input = QLineEdit()
        self.rfbt_input.setFixedWidth(80)
        self.rfbb_label = QLabel("Rfbb(kΩ):")
        self.rfbb_input = QLineEdit()
        self.rfbb_input.setFixedWidth(80)
        self.calc_resistor_btn = QPushButton("Result")
        self.calc_resistor_btn.setFixedWidth(100)

        # pos
        input_grid.addWidget(self.vout_label, 0, 0)
        input_grid.addWidget(self.vout_input, 0, 1)
        input_grid.addWidget(self.vfb_label, 0, 2)
        input_grid.addWidget(self.vfb_input, 0, 3)
        input_grid.addWidget(self.calc_voltage_btn, 0, 4)

        input_grid.addWidget(self.rfbt_label, 1, 0)
        input_grid.addWidget(self.rfbt_input, 1, 1)
        input_grid.addWidget(self.rfbb_label, 1, 2)
        input_grid.addWidget(self.rfbb_input, 1, 3)
        input_grid.addWidget(self.calc_resistor_btn, 1, 4)

        # 设置列间距
        input_grid.setHorizontalSpacing(20)

        # 添加到主布局
        input_layout.addLayout(input_grid)

        # 误差范围
        error_layout = QHBoxLayout()
        self.error_label = QLabel("Err Range:")
        self.error_combo = QComboBox()
        self.error_combo.addItems([str(i) for i in range(1, 11)])
        self.error_combo.setCurrentText("5")
        error_layout.addWidget(self.error_label)
        error_layout.addWidget(self.error_combo)
        error_layout.addStretch()
        input_layout.addLayout(error_layout)

        layout.addLayout(input_layout)

        # 过滤选项
        self.filter_check = QCheckBox("Filter out resistors below 1kΩ")
        self.filter_check.setChecked(True)
        layout.addWidget(self.filter_check)

        # 结果显示区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        # 添加关闭按钮
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        # 连接信号
        self.voltage_mode.toggled.connect(self.toggle_mode)
        self.calc_voltage_btn.clicked.connect(self.calculate_combinations)
        self.calc_resistor_btn.clicked.connect(self.calculate_voltage)
        self.filter_check.stateChanged.connect(self.filter_results)

        # 初始化界面状态
        self.toggle_mode()

    def toggle_mode(self):
        is_voltage_mode = self.voltage_mode.isChecked()
        self.vout_input.setEnabled(is_voltage_mode)
        self.vfb_input.setEnabled(is_voltage_mode)
        self.error_combo.setEnabled(is_voltage_mode)
        self.calc_voltage_btn.setEnabled(is_voltage_mode)

        self.rfbt_input.setEnabled(not is_voltage_mode)
        self.rfbb_input.setEnabled(not is_voltage_mode)
        self.calc_resistor_btn.setEnabled(not is_voltage_mode)

    def filter_results(self):
        if self.voltage_mode.isChecked():
            self.calculate_combinations()
        else:
            self.calculate_voltage()

    def calculate_combinations(self):
        try:
            vout = float(self.vout_input.text())
            vfb = float(self.vfb_input.text())
            error_percent = float(self.error_combo.currentText())

            resistor_list = self.read_resistor_list()
            results = []

            for rfbb in resistor_list:
                for rfbt in resistor_list:
                    actual_vout = vfb * (1 + rfbt / rfbb)
                    error = ((actual_vout - vout) / vout) * 100

                    if abs(error) <= error_percent:
                        if not self.filter_check.isChecked() or (
                            rfbt >= 1000 and rfbb >= 1000
                        ):
                            results.append((rfbt, rfbb, error))

            # 按照 Rfbt 从小到大排序
            results.sort(key=lambda x: x[0])

            self.result_text.clear()

            for rfbt, rfbb, error in results:
                actual_vout = vfb * (1 + rfbt / rfbb)
                self.result_text.append(
                    f"Rfbt(Vout) = {self.format_resistance(rfbt)}, "
                    f"Rfbb(Gnd) = {self.format_resistance(rfbb)}, "
                    f"Err = {'+' if error > 0 else ''}{error:.1f}%, "
                    f"Vout = {actual_vout:.3f}V"
                )

        except ValueError:
            self.result_text.setText("Please enter valid numbers")

    def calculate_voltage(self):
        try:
            rfbt = float(self.rfbt_input.text()) * 1000
            rfbb = float(self.rfbb_input.text()) * 1000
            vfb = float(self.vfb_input.text())
            actual_vout = vfb * (1 + rfbt / rfbb)

            self.result_text.clear()
            self.result_text.append(
                f"Rfbt = {self.format_resistance(rfbt)}, "
                f"Rfbb = {self.format_resistance(rfbb)}, "
                f"Vout = {actual_vout:.3f}V"
            )
        except ValueError:
            self.result_text.setText("Please enter valid numbers")


def main():
    app = QApplication(sys.argv)
    calculator = ResistorCalculator()
    calculator.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
