public with sharing class StudentApplicationController {
    @AuraEnabled
    public static String submitApplication(String firstName, String lastName, String email) {
        Contact student = new Contact(
            FirstName = firstName,
            LastName = lastName,
            Email = email
        );
        insert student;
        return student.Id;
    }
}