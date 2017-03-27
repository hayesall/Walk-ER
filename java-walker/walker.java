// import java.util.*;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.LinkedHashMap;

public class walker {
    public static void main(String[] args) {

	LinkedHashMap ER_graph = new LinkedHashMap();
	LinkedHashMap attributes = new LinkedHashMap();

	// Help Menu
	String helpmenu = String.join("\n"
				      , "NAME"
				      , "    Walk-ER vBeta0.4"
				      , ""
				      , "SYNOPSIS"
				      , "    $ javac walker.java"
				      , "    $ java walker [OPTIONS]"
				      , ""
				      , "DESCRIPTION"
				      , "    \"Walker\" for Entity-Relational Diagrams, originally from ERDPlus."
				      , ""
				      , "OPTIONS"
				      , "    -h, --help: Print a message that briefly summarizes options, then exits."
				      );

	if ((args.length == 0) || (Arrays.asList(args).contains("-h")) || (Arrays.asList(args).contains("--help"))) {
	    // java walker -h | java walker --help | java walker
	    System.out.println(helpmenu);
	    System.exit(0);
	}
	
	ER_graph.put(1, "professorid");
	ER_graph.put(10, "courseid");
	ER_graph.put(6, "studentid");

	String[] firstList = {"True", "1"};
	String[] secondList = {"True", "10"};
	//ER_graph.put("Salary", firstList);
	ER_graph.put("Salary", new Integer[] {1,2,3});
	// Might implement a try/catch block in case there are different data types.
	// Array.toString(arr) and Array.deepToString(arr) are both built in implementations that could be useful for printing if necessary.
	System.out.println(new Integer[] {1,2,3});
	System.out.println(Arrays.toString(new Integer[] {1,2,3}));
	System.out.println(Arrays.toString(firstList));

	//	Set set = ER_graph.entrySet();
	//Iterator i = set.iterator();
	
	// Display the elements from the hashmap
	//while(i.hasNext()) {
	//    Map.Entry me= (Map.Entry)i.next();
	//    System.out.print(me.getKey() + ": ");
	//    System.out.println(me.getValue());
	//}
    }
}
