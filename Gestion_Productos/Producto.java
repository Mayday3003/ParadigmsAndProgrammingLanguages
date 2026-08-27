package Gestion_Productos;

/**
 * Clase que representa un Producto en el sistema de la tienda.
 * En Java, una clase es una plantilla para crear objetos. Cada objeto tiene
 * atributos (variables) y comportamientos (métodos).
 */
public class Producto {
    // Atributos privados: solo se pueden acceder dentro de esta clase (encapsulación)
    private String nombre;
    private double precio;
    private int stock;
    private String categoria;

    /**
     * Constructor: Método especial que se ejecuta al crear un nuevo producto con "new Producto(...)".
     * Sirve para inicializar los atributos de la clase.
     */
    public Producto(String nombre, double precio, int stock, String categoria) {
        this.nombre = nombre;
        this.precio = precio;
        this.stock = stock;
        this.categoria = categoria;
    }

    // ==========================================
    // GETTERS (Métodos para obtener los valores)
    // ==========================================

    public String getNombre() {
        return nombre;
    }

    public double getPrecio() {
        return precio;
    }

    public int getStock() {
        return stock;
    }

    public String getCategoria() {
        return categoria;
    }

    // ==========================================
    // SETTERS (Métodos para modificar los valores)
    // ==========================================

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public void setPrecio(double precio) {
        this.precio = precio;
    }

    public void setStock(int stock) {
        this.stock = stock;
    }

    public void setCategoria(String categoria) {
        this.categoria = categoria;
    }

    /**
     * toString(): Método que Java usa automáticamente cuando queremos representar
     * el objeto como una cadena de texto (por ejemplo, al usar System.out.println).
     */
    @Override
    public String toString() {
        return "Producto{" +
                "nombre='" + nombre + '\'' +
                ", precio=" + precio +
                ", stock=" + stock +
                ", categoria='" + categoria + '\'' +
                '}';
    }
}