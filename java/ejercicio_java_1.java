
// Imperativo
import java.util.*;

public class ejercicio_java_1 {

    public static void main(String[] args) {
        List<Integer> numeros = Arrays.asList(0,4,5,6,7);

        int maximo = numeros.get(0);
        for (Integer n : numeros){
            if (n > maximo) {
                maximo = n;

            }
                
        }
    System.out.println("El numero maximo es" + maximo);
}

}

