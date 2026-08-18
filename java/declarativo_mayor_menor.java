import java.util.List;
import java.util.stream.Collectors;

public class declarativo_mayor_menor {

    public static String main(){

    List<Integer> edades = List.of(5);

    List<Integer> mayor_menor = edades.stream()
        .filter(e -> e <= 18)
        .collect(Collectors.toList());

        if (mayor_menor.isEmpty()) {
            return "Eres mayor de edad";
        } else {
            return "Eres menor de edad";
        }
}

}