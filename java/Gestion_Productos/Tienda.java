package Gestion_Productos;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.stream.Collectors;
import java.util.function.Supplier;
import java.util.function.Predicate;
import java.util.function.Function;
import java.util.function.Consumer;
import java.util.function.BiFunction;
import java.util.function.BiPredicate;
import java.util.function.BiConsumer;
import java.util.function.UnaryOperator;
import java.util.function.BinaryOperator;

/**
 * Clase principal que ejecuta la lógica de la tienda usando Programación Funcional en Java.
 * Java introduce interfaces funcionales en Java 8 para poder usar expresiones lambda (funciones anónimas).
 */
public class Tienda {

    public static void main(String[] args) throws Exception {

        // 1. Inicialización de la lista de productos
        // Usamos ArrayList para tener una lista dinámica a la que le podamos agregar elementos más adelante.
        List<Producto> productos = new ArrayList<>(Arrays.asList(
                new Producto("Laptop", 3500.0, 8, "Tecnología"),
                new Producto("Mouse", 80.0, 25, "Tecnología"),
                new Producto("Teclado", 150.0, 10, "Tecnología"),
                new Producto("Silla", 600.0, 4, "Hogar"),
                new Producto("Escritorio", 1200.0, 3, "Hogar")
        ));

        // =========================================================================
        // 1. Supplier<T> : Generar un producto nuevo
        // Explicación: Un Supplier (Proveedor) no recibe ningún argumento, pero retorna un valor de tipo T.
        // En este caso, retorna un nuevo objeto Producto cuando llamamos a .get().
        // =========================================================================
        Supplier<Producto> proveedorProducto = () -> new Producto("Monitor", 900.0, 6, "Tecnología");

        Producto nuevoProducto = proveedorProducto.get(); // Crea el producto
        productos.add(nuevoProducto); // Lo agregamos a nuestra lista
        System.out.println("1. [Supplier] Producto nuevo agregado: " + nuevoProducto);


        // =========================================================================
        // 2. Predicate<T> : Filtrar productos caros (precio > 500)
        // Explicación: Un Predicate (Predicado) recibe un argumento de tipo T y devuelve un booleano (true/false).
        // Se usa principalmente para realizar filtros en flujos de datos (Streams).
        // =========================================================================
        Predicate<Producto> esCaro = producto -> producto.getPrecio() > 500;

        // Filtramos la lista usando streams:
        // .stream() convierte la lista en un flujo de datos.
        // .filter(esCaro) mantiene en el flujo solo los elementos que cumplen la condición.
        // .collect(Collectors.toList()) guarda el resultado en una nueva lista.
        List<Producto> productosCaros = productos.stream()
                .filter(esCaro)
                .collect(Collectors.toList());

        System.out.println("\n2. [Predicate] Productos caros (precio > 500):");
        productosCaros.forEach(p -> System.out.println("   - " + p.getNombre() + ": $" + p.getPrecio()));


        // =========================================================================
        // 3. Function<T, R> : Obtener el nombre del producto
        // Explicación: Una Function recibe un argumento de tipo T y lo transforma en un resultado de tipo R.
        // Aquí transformamos un 'Producto' en un 'String' (su nombre).
        // Producto::getNombre es una referencia a método equivalente a (p) -> p.getNombre()
        // =========================================================================
        Function<Producto, String> obtenerNombre = Producto::getNombre;

        // .map(obtenerNombre) aplica la transformación a cada elemento del flujo.
        List<String> nombres = productos.stream()
                .map(obtenerNombre)
                .collect(Collectors.toList());

        System.out.println("\n3. [Function] Nombres de todos los productos:");
        System.out.println("   " + nombres);


        // =========================================================================
        // 4. Consumer<T> : Mostrar producto
        // Explicación: Un Consumer (Consumidor) recibe un argumento de tipo T, realiza una acción y no retorna nada.
        // Se usa mucho para impresión o para guardar datos externamente.
        // =========================================================================
        Consumer<Producto> mostrarProducto = producto -> System.out.println("   " + producto);

        System.out.println("\n4. [Consumer] Listado completo de productos:");
        productos.forEach(mostrarProducto); // forEach ejecuta el Consumer para cada producto


        // =========================================================================
        // 5. BiFunction<T, U, R> : Calcular precio con descuento
        // Explicación: Recibe dos argumentos (de tipos T y U) y retorna un resultado de tipo R.
        // Aquí recibe: (Precio base [Double], Porcentaje de descuento [Double]) y retorna el Precio Final [Double].
        // =========================================================================
        BiFunction<Double, Double, Double> aplicarDescuento = 
                (precio, descuento) -> precio - (precio * descuento / 100);

        double precioFinalLaptop = aplicarDescuento.apply(3500.0, 10.0);
        System.out.println("\n5. [BiFunction] Laptop (base $3500) con 10% de descuento: $" + precioFinalLaptop);


        // =========================================================================
        // 6. BiPredicate<T, U> : Validar si hay stock suficiente para una compra
        // Explicación: Recibe dos argumentos (T y U) y retorna un booleano (true/false).
        // Aquí recibe: (El Producto, La Cantidad solicitada) y valida si el stock es suficiente.
        // =========================================================================
        BiPredicate<Producto, Integer> stockSuficiente = 
                (producto, cantidad) -> producto.getStock() >= cantidad;

        Producto mouse = productos.get(1); // El segundo producto es el Mouse
        int cantidadAComprar = 20;
        boolean hayStock = stockSuficiente.test(mouse, cantidadAComprar);
        System.out.println("\n6. [BiPredicate] ¿Hay stock suficiente de " + mouse.getNombre() + 
                           " (Stock actual: " + mouse.getStock() + ") para comprar " + cantidadAComprar + " unidades? " + hayStock);


        // =========================================================================
        // 7. BiConsumer<T, U> : Actualizar stock después de vender
        // Explicación: Recibe dos argumentos (T y U), realiza una acción modificando el estado y no retorna nada.
        // Aquí recibe: (El Producto, La Cantidad a restar del stock).
        // =========================================================================
        BiConsumer<Producto, Integer> venderProducto = 
                (producto, cantidad) -> producto.setStock(producto.getStock() - cantidad);

        int cantidadAVender = 5;
        System.out.println("\n7. [BiConsumer] Intentando vender " + cantidadAVender + " unidades de " + mouse.getNombre() + "...");
        if (stockSuficiente.test(mouse, cantidadAVender)) {
            venderProducto.accept(mouse, cantidadAVender); // Ejecuta el descuento del stock
            System.out.println("   ¡Venta realizada con éxito! Nuevo stock de " + mouse.getNombre() + ": " + mouse.getStock());
        } else {
            System.out.println("   Error: No hay suficiente stock para realizar la venta.");
        }


        // =========================================================================
        // 8. UnaryOperator<T> : Aumentar precio en 5%
        // Explicación: Es una especialización de Function donde el argumento de entrada y el de retorno son del mismo tipo T.
        // Modifica el precio del producto y lo devuelve.
        // =========================================================================
        UnaryOperator<Producto> aumentarPrecio = producto -> {
            producto.setPrecio(producto.getPrecio() * 1.05);
            return producto;
        };

        // Aplicamos el incremento a todos los productos directamente en la lista original.
        // replaceAll modifica cada elemento en su lugar usando el UnaryOperator.
        // Esto evita reasignar la variable 'productos', manteniéndola "effectively final".
        productos.replaceAll(aumentarPrecio);

        System.out.println("\n8. [UnaryOperator] Productos después de aplicar el 5% de aumento general:");
        productos.forEach(mostrarProducto);


        // =========================================================================
        // 9. BinaryOperator<T> : Sumar precios de dos productos
        // Explicación: Es una especialización de BiFunction donde los dos parámetros y el resultado son del mismo tipo T.
        // En este caso, toma dos precios (Double, Double) y devuelve su suma (Double).
        // Double::sum es una referencia a método equivalente a (a, b) -> Double.sum(a, b)
        // =========================================================================
        BinaryOperator<Double> sumarPrecios = Double::sum;

        double precioLaptopActual = productos.get(0).getPrecio();
        double precioMouseActual = productos.get(1).getPrecio();
        double sumaDosProductos = sumarPrecios.apply(precioLaptopActual, precioMouseActual);
        
        System.out.printf("\n9. [BinaryOperator] Suma del precio actual de %s ($%.2f) y %s ($%.2f): $%.2f\n",
                productos.get(0).getNombre(), precioLaptopActual, 
                productos.get(1).getNombre(), precioMouseActual, 
                sumaDosProductos);


        // =========================================================================
        // 10. Runnable : Tarea sin retorno
        // Explicación: Representa una tarea que se puede ejecutar pero que no toma parámetros y no devuelve ningún valor.
        // Generalmente se usa para tareas asíncronas o de ejecución directa simple.
        // =========================================================================
        Runnable tareaResumen = () -> {
            System.out.println("\n10. [Runnable] Generando reporte final...");
            System.out.println("    Reporte: Todos los procesos funcionales han sido ejecutados con éxito.");
        };
        tareaResumen.run(); // Ejecuta la tarea


        // =========================================================================
        // 11. Callable<V> : Tarea con retorno (Calcular valor total del inventario)
        // Explicación: Representa una tarea que devuelve un resultado de tipo V y puede lanzar excepciones.
        // Se usa mucho en programación concurrente (hilos), pero también como tarea computable genérica.
        // =========================================================================
        Callable<Double> calcularValorInventario = () ->
                productos.stream()
                        .map(p -> p.getPrecio() * p.getStock()) // Multiplicamos precio por stock de cada producto
                        .reduce(0.0, Double::sum); // Sumamos todos los resultados empezando desde 0.0

        Double valorInventario = calcularValorInventario.call(); // Ejecuta la tarea y obtiene el resultado
        System.out.printf("\n11. [Callable] Valor total de inventario calculado: $%.2f\n", valorInventario);
    }
}
