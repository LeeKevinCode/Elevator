package com.nexwah;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

import javax.servlet.http.*;

import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;

@SuppressWarnings("serial")
public class TestAppEngineServlet extends HttpServlet {
	public void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
		resp.setContentType("text/plain");
		resp.getWriter().println("Hello, world");
	}

	public void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
		resp.setContentType("text/plain");
		// String inputDate = req.getParameter("date");
		String laserData = req.getParameter("laserData");
		String rms = req.getParameter("rms");
		String rtc = req.getParameter("rtc");
		String temp = req.getParameter("temp");
		String cur = req.getParameter("cur");
		String hum = req.getParameter("hum");

		SimpleDateFormat dtFormate = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss:SSS");
		DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();

		laserData = laserData.substring(12, laserData.length() - 2);
		String[] laserDetecter = laserData.split(" ");
		Date rtcDate = parseRTC(rtc);
		Date[] rtcSet = genDateSet(rtcDate, laserDetecter.length, 30);

		for (int i = 0; i < laserDetecter.length; i++) {

			Entity elevator = new Entity("Elevator");
			if (laserDetecter[i].length() < 6) {
				laserDetecter[i] = "Error" + laserDetecter[i];
			}
			elevator.setProperty("laserDetecter", laserDetecter[i]);
			elevator.setProperty("rms", rms);
			elevator.setProperty("rtc", dtFormate.format(rtcSet[i]));
			elevator.setProperty("temp", temp);
			elevator.setProperty("cur", cur);
			elevator.setProperty("hum", hum);

			datastore.put(elevator);
		}
		resp.getWriter().println("Very Good");

	}

	public Date parseRTC(String rtc) {
		SimpleDateFormat dForm = new SimpleDateFormat("(yyyy, MM,dd, uu, hh, mm, ss, SSS)");
		Date date = null;

		try {
			date = dForm.parse(rtc);
		} catch (ParseException e) {
			return null;
		}

		SimpleDateFormat dFormSSS = new SimpleDateFormat("SSS");
		String SSS = dFormSSS.format(date);
		int miliSec = Integer.valueOf(SSS);

		long time = date.getTime();
		time = time - miliSec + miliSec * 1000 / 256;
		date.setTime(time);
		return date;
	}

	public Date[] genDateSet(Date date, int realNum, int expectNum) {
		if (realNum <= 0) {
			return null;
		}
		Date[] dateSet = new Date[realNum];
		long firstTime = date.getTime() - expectNum * 1000;
		long interval = expectNum * 1000 / realNum;
		System.out.println(interval);
		for (int i = 0; i < realNum; i++) {
			firstTime += interval;
			dateSet[i] = new Date(firstTime);
		}
		return dateSet;
	}
}
