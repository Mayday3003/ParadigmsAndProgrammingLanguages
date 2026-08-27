package reto;

import java.io.PrintStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.function.BiConsumer;
import java.util.function.BiFunction;
import java.util.function.BiPredicate;
import java.util.function.BinaryOperator;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.function.Supplier;
import java.util.function.UnaryOperator;
import java.util.stream.Collectors;

//Realizar un programa en Java con programación funcional:

//1. crear empleados,
//2. filtrar por salario, área o antigüedad,
//3. calcular bonificaciones,
//4. validar si un empleado aplica a un beneficio,
//5. actualizar salarios,
//6. acumular masa salarial,
//7. ejecutar reportes.

public class Empleado {
    private String nombre;
    private String area;
    private double salario;
    private int antiguedad;

    public Empleado(String nombre, String area, double salario, int antiguedad) {
        this.nombre = nombre;
        this.area = area;
        this.salario = salario;
        this.antiguedad = antiguedad;
    }

    public String getNombre() {
        return nombre;
    }

    public String getArea() {
        return area;
    }

    public double getSalario() {
        return salario;
    }

    public int getAntiguedad() {
        return antiguedad;
    }

    public void setSalario(double salario) {
        this.salario = salario;
    }
    

    
}
