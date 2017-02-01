package com.nexwah;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.TimeZone;

import javax.servlet.http.*;

@SuppressWarnings("serial")
public class ShowTime extends HttpServlet{
	
	public void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
		resp.setContentType("text/plain");
		TimeZone.setDefault(TimeZone.getTimeZone("Singapore"));
		SimpleDateFormat sdf = new SimpleDateFormat("yyyy,MM,dd,uu,HH,mm,ss,");
		Date dt = new Date();
		String result = sdf.format(dt);
		result = "##" + result + "0";
		resp.getWriter().println(result);
	}

}
