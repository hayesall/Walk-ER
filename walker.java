import java.util.*;
// import java.util.LinkedHashMap;

public class walker {
    public static void main(String[] args) {

	LinkedHashMap ER_graph = new LinkedHashMap();
	LinkedHashMap attributes = new LinkedHashMap();

	ER_graph.put(1, "professorid");
	ER_graph.put(10, "courseid");
	ER_graph.put(6, "studentid");

	String[] firstList = {"True", "1"};
	//ER_graph.put("Salary", firstList);
	ER_graph.put("Salary", new Integer[] {1,2,3});
	// Might implement a try/catch block in case there are different data types.
	// Array.toString(arr) and Array.deepToString(arr) are both built in implementations that could be useful for printing if necessary.
	System.out.println(new Integer[] {1,2,3});
	System.out.println(Arrays.toString(firstList));

	Set set = ER_graph.entrySet();
	Iterator i = set.iterator();
	
	// Display the elements from the hashmap
	while(i.hasNext()) {
	    Map.Entry me= (Map.Entry)i.next();
	    System.out.print(me.getKey() + ": ");
	    System.out.println(me.getValue());
	}
    }
}
