package com.nexwah;

import java.util.Map;
import java.util.TreeMap;

public class MyTreeMap<K, V> extends TreeMap<K, V>{
	private static final long serialVersionUID = 1L;
    private static final char LEFT = '[';
    private static final char RIGHT = ']';
    private static final char COMMA = ',';
    
	@Override
	public String toString(){
		
		StringBuilder keys = new StringBuilder();
		StringBuilder values = new StringBuilder();
		
		keys.append(LEFT);
		values.append(LEFT);
		for (Map.Entry<K, V> entry : this.entrySet()) {
			keys.append(entry.getKey());
			keys.append(COMMA);
			values.append(LEFT);
			values.append(entry.getKey());
			values.append(COMMA);
			values.append(entry.getValue());
			values.append(RIGHT);
			values.append(COMMA);
        }
		keys.deleteCharAt(keys.length()-1);
		values.deleteCharAt(values.length()-1);
		keys.append(RIGHT);
		values.append(RIGHT);
        return "" + LEFT + keys + COMMA + values + RIGHT;
	}
}
