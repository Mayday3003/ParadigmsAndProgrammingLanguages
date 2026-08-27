//Realizar un programa en Java con programación funcional:

//1. crear empleados,
//2. filtrar por salario, área o antigüedad,
//3. calcular bonificaciones,
//4. validar si un empleado aplica a un beneficio,
//5. actualizar salarios,
//6. acumular masa salarial,
//7. ejecutar reportes.
package reto;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Empresa {

    public static void main(String[] args) throws Exception {
        // Crear una lista de empleados
        List<Empleado> empleados = new ArrayList<>(Arrays.asList(
            new Empleado("Juan", "Ventas", 2000000, 5),
            new Empleado("Ana", "Marketing", 3500000, 3),
            new Empleado("Luis", "ML", 4000000.0, 7)
        ));

        //1. crear empleados

        java.util.function.Supplier<Empleado> proveedorEmpleado = () -> new Empleado("Carlos", "Arte", 4500000, 3); 
        Empleado nuevoEmpleado = proveedorEmpleado.get(); 
        empleados.add(nuevoEmpleado);
        System.out.println("1. Empleado nuevo agregado: " + nuevoEmpleado.getNombre() + ", Área: " + nuevoEmpleado.getArea() + ", Salario: " + nuevoEmpleado.getSalario() + ", Antigüedad: " + nuevoEmpleado.getAntiguedad());



        //2. filtrar por salario, área o antigüedad -  filter(Predicate)

        java.util.function.Predicate<Empleado> filtroSalario = e -> e.getSalario() > 3500000.0;
        java.util.function.Predicate<Empleado> filtroArea = e -> e.getArea().equals("Marketing");
        java.util.function.Predicate<Empleado> filtroAntiguedad = e -> e.getAntiguedad() > 5;

        List<Empleado> empleadosFiltrados = empleados.stream()
                .filter(filtroSalario.or(filtroArea).or(filtroAntiguedad))
                .collect(java.util.stream.Collectors.toList());
        
        System.out.println("2. [Predicate] Empleados filtrados (Salario > 3500000, Área: Marketing, o Antigüedad > 5):");
        empleadosFiltrados.forEach(e -> System.out.println("   - " + e.getNombre() + ", Área: " + e.getArea() + ", Salario: " + e.getSalario() + ", Antigüedad: " + e.getAntiguedad()));

        //3. calcular bonificaciones
        java.util.function.Function<Empleado, Double> calcularBonificacion = e -> e.getSalario() * 0.10; // 10% de bonificación
        System.out.println("3. [Function] Bonificaciones calculadas:");
        empleados.forEach(e -> {
            double bonificacion = calcularBonificacion.apply(e);
            System.out.println("   - " + e.getNombre() + ": Bonificación = " + bonificacion);
        }); 


        //4. validar si un empleado aplica a un beneficio.

        java.util.function.Predicate<Empleado> aplicaBeneficio = e -> e.getAntiguedad() > 3; 
        System.out.println("4. [Predicate] Validación de beneficios:");

        empleados.forEach(e -> {
            boolean aplica = aplicaBeneficio.test(e);
            System.out.println("   - " + e.getNombre() + ": Aplica a beneficio? " + (aplica ? "Sí" : "No"));
        });


        java.util.function.Consumer<Empleado> actualizarSalario = e -> e.setSalario(e.getSalario() * 1.05); 
        System.out.println("5.Actualización de salarios (Aumento del 5% para empleados con antigüedad > 3 años):");
        empleados.forEach(e -> {
            if (e.getAntiguedad() > 3) {
                actualizarSalario.accept(e);
                System.out.println("   - " + e.getNombre() + ": Nuevo salario = " + e.getSalario());
            }
        });


        //6. acumular masa salarial 
        java.util.function.BinaryOperator<Double> acumularMasaSalarial = (total, salario) -> total + salario;
        double masaSalarialTotal = empleados.stream()
                .map(e -> e.getSalario() + calcularBonificacion.apply(e)) // Sumar salario + bonificación
                .reduce(0.0, acumularMasaSalarial);
        System.out.println("6. [BinaryOperator] Masa salarial total (incluyendo bonificaciones): " + masaSalarialTotal);


        //7. Ejecutar reportes 
        java.util.function.Consumer<List<Empleado>> generarReporte = lista -> {
            System.out.println("7. [Consumer] Reporte de empleados:");
            lista.forEach(e -> System.out.println("   - " + e.getNombre() + ", Área: " + e.getArea() + ", Salario: " + e.getSalario() + ", Antigüedad: " + e.getAntiguedad()));
        };
        generarReporte.accept(empleados);
    }
}