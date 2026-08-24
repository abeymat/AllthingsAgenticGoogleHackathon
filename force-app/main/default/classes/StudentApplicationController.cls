public with sharing class StudentApplicationController {

    @AuraEnabled
    public static String createStudentApplication(String firstName, String lastName, String email, String phone, String program, String notes) {
        try {
            if (String.isBlank(lastName)) {
                throw new AuraHandledException('Last Name is required.');
            }

            Contact newStudent = new Contact(
                FirstName = firstName,
                LastName = lastName,
                Email = email,
                Phone = phone,
                Description = 'Applied Program: ' + (String.isNotBlank(program) ? program : 'N/A') + 
                              (String.isNotBlank(notes) ? '\nNotes: ' + notes : '')
            );

            insert newStudent;
            return newStudent.Id;
        } catch (Exception e) {
            throw new AuraHandledException('Error creating student application: ' + e.getMessage());
        }
    }
}