import java.util.Arrays;
import java.util.List;

public 
// Declarativo

public class ejercicio_java_2 {

    public static void main(String[] args) {
        List<Integer> numeros = Arrays.asList(0,4,5,6,7);

        int maximo = numeros.stream()
                            .max(Integer::compare)
                            .get(); // Obtener el valor máximo usando un stream y un comparador
        System.out.println("El numero maximo es" + maximo);
    }

} {
    
}
