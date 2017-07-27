
import java.util.Date;

public class Welcome {
	public static void main(String[] args) {

		Date date = new Date();
		System.out.println("Welcome to Java!");
		System.out.println("Welcome to Java! " + date.getTime());
		System.out.println("Welcome to Java! " + date.toString());
	}
}
