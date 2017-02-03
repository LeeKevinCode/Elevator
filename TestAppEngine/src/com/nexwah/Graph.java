package com.nexwah;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;
import com.google.appengine.api.datastore.PreparedQuery;
import com.google.appengine.api.datastore.Query;

@SuppressWarnings("serial")
public class Graph extends HttpServlet {

	public void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
		DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();

		Query q = new Query("Elevator");

		PreparedQuery pq = datastore.prepare(q);
		MyTreeMap<Long, Integer> map = new MyTreeMap<Long, Integer>();
		SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss:SSS");
		
		for (Entity result : pq.asIterable()) {
			String rtc = (String) result.getProperty("rtc");
			String ld = (String) result.getProperty("laserDetecter");
			
			try {
				Date dt = sdf.parse(rtc);
				long time = dt.getTime();
				Double dld = new Double(ld);
				dld *= 1000;
				int fld = dld.intValue();
				map.put(time, fld);
			} catch (Exception e) {

			}
		}
		
		resp.getWriter().append(map.toString());

	}

}
