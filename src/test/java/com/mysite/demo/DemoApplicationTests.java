package com.mysite.demo;


class Mom {
	static int x;
	Mom() {
		x = 40;
	}
	public void setX(int x) {
		this.x = x;
	}
	public void printX() {
		System.out.println(x);
	}
	public void printXX() {
		System.out.println(this.x);
	}
}
class DemoApplicationTests extends Mom {
	private int x;	
	
	DemoApplicationTests() {
		x = 50;
	}
	public void setX(int x) {
		this.x = x;
	}
	public void printXX() {
		System.out.println(super.x);
	}

	public static void main(String[] args) {
		Mom t = new DemoApplicationTests();
		t.setX(90);
		t.printXX();
	}

}
