import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

public class DemoEventos {

    private static int contador = 0;
    private static JLabel contadorLabel;
    private static JLabel ultimoEventoLabel;
    private static final DateTimeFormatter TIME_FMT = DateTimeFormatter.ofPattern("HH:mm:ss");

    public static void main(String[] args) {
        // Lanzamos la creación de la GUI en el Event Dispatch Thread (EDT)
        SwingUtilities.invokeLater(() -> createAndShowGUI());
    }

    private static void createAndShowGUI() {
        JFrame frame = new JFrame("Demo: Programación Orientada a Eventos");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(500, 400);
        frame.setLayout(new BorderLayout(10, 10));

        // Etiqueta grande con el contador (centrada)
        contadorLabel = new JLabel(String.valueOf(contador), SwingConstants.CENTER);
        contadorLabel.setFont(new Font("SansSerif", Font.BOLD, 72));
        frame.add(contadorLabel, BorderLayout.CENTER);

        // Etiqueta pequeña para mostrar el último evento ocurrido
        ultimoEventoLabel = new JLabel("Último evento: ninguno", SwingConstants.CENTER);
        ultimoEventoLabel.setFont(new Font("SansSerif", Font.PLAIN, 30));
        frame.add(ultimoEventoLabel, BorderLayout.NORTH);

        // Panel inferior con los tres botones: +1, -1 y Reiniciar
        JPanel panelBotones = new JPanel(new GridLayout(1, 3, 10, 10));
        JButton btnMas = new JButton("+1");
        JButton btnMenos = new JButton("-1");
        JButton btnReiniciar = new JButton("Reiniciar");
        Font botonFont = new Font("SansSerif", Font.PLAIN, 18);
        btnMas.setFont(botonFont);
        btnMenos.setFont(botonFont);
        btnReiniciar.setFont(botonFont);
        panelBotones.add(btnMenos);
        panelBotones.add(btnReiniciar);
        panelBotones.add(btnMas);
        frame.add(panelBotones, BorderLayout.SOUTH);

        // Ajustes estéticos: color de fondo inicial
        updateBackgroundColor(frame);

        // --- Listeners con lambdas y comentarios en español ---

        // Fuente: botón '+1' (objeto JButton 'btnMas')
        // Evento: ActionEvent disparado al pulsar el botón
        // Acción: incrementa el contador en 1, actualiza etiquetas y color de fondo
        btnMas.addActionListener(e -> {
            contador++;
            contadorLabel.setText(String.valueOf(contador));
            String hora = LocalTime.now().format(TIME_FMT);
            String fuente = ((JButton) e.getSource()).getText();
            ultimoEventoLabel.setText("Último evento: " + e.getClass().getSimpleName() + " en botón " + fuente + " a las " + hora);
            updateBackgroundColor(frame);
        });

        // Fuente: botón '-1' (objeto JButton 'btnMenos')
        // Evento: ActionEvent disparado al pulsar el botón
        // Acción: decrementa el contador en 1, actualiza etiquetas y color de fondo
        btnMenos.addActionListener(e -> {
            contador--;
            contadorLabel.setText(String.valueOf(contador));
            String hora = LocalTime.now().format(TIME_FMT);
            String fuente = ((JButton) e.getSource()).getText();
            ultimoEventoLabel.setText("Último evento: " + e.getClass().getSimpleName() + " en botón " + fuente + " a las " + hora);
            updateBackgroundColor(frame);
        });

        // Fuente: botón 'Reiniciar' (objeto JButton 'btnReiniciar')
        // Evento: ActionEvent disparado al pulsar el botón
        // Acción: pone el contador a 0, actualiza etiquetas y color de fondo
        btnReiniciar.addActionListener(e -> {
            contador = 0;
            contadorLabel.setText(String.valueOf(contador));
            String hora = LocalTime.now().format(TIME_FMT);
            String fuente = ((JButton) e.getSource()).getText();
            ultimoEventoLabel.setText("Último evento: " + e.getClass().getSimpleName() + " en botón " + fuente + " a las " + hora);
            updateBackgroundColor(frame);
        });

        // Mostrar la ventana centrada
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
    }

    // Actualiza el color de fondo del contenedor según el valor del contador:
    // positivo -> verde claro, negativo -> rojo claro, cero -> gris claro
    private static void updateBackgroundColor(JFrame frame) {
        Color color;
        if (contador > 0) {
            color = new Color(200, 255, 200); // verde claro
        } else if (contador < 0) {
            color = new Color(255, 220, 220); // rojo claro
        } else {
            color = new Color(240, 240, 240); // gris claro
        }
        frame.getContentPane().setBackground(color);
        // Forzar repintado para que el cambio de color sea inmediato
        frame.getContentPane().repaint();
    }
}
