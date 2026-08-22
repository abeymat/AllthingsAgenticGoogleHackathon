import { LightningElement, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { createRecord } from 'lightning/uiRecordApi';
import CONTACT_OBJECT from '@salesforce/schema/Contact';
import FIRST_NAME_FIELD from '@salesforce/schema/Contact.FirstName';
import LAST_NAME_FIELD from '@salesforce/schema/Contact.LastName';
import EMAIL_FIELD from '@salesforce/schema/Contact.Email';
import PHONE_FIELD from '@salesforce/schema/Contact.Phone';
import TITLE_FIELD from '@salesforce/schema/Contact.Title';

export default class StudentApplicationForm extends LightningElement {
    @track firstName = '';
    @track lastName = '';
    @track email = '';
    @track phone = '';
    @track title = 'Student Applicant';
    isLoading = false;

    handleInputChange(event) {
        const field = event.target.dataset.field;
        if (field === 'firstName') {
            this.firstName = event.target.value;
        } else if (field === 'lastName') {
            this.lastName = event.target.value;
        } else if (field === 'email') {
            this.email = event.target.value;
        } else if (field === 'phone') {
            this.phone = event.target.value;
        } else if (field === 'title') {
            this.title = event.target.value;
        }
    }

    handleSubmit() {
        if (!this.validateForm()) {
            this.dispatchEvent(
                new ShowToastEvent({
                    title: 'Validation Error',
                    message: 'Please complete all required fields correctly.',
                    variant: 'error'
                })
            );
            return;
        }

        this.isLoading = true;

        const fields = {};
        fields[FIRST_NAME_FIELD.fieldApiName] = this.firstName;
        fields[LAST_NAME_FIELD.fieldApiName] = this.lastName;
        fields[EMAIL_FIELD.fieldApiName] = this.email;
        fields[PHONE_FIELD.fieldApiName] = this.phone;
        fields[TITLE_FIELD.fieldApiName] = this.title;

        const recordInput = { apiName: CONTACT_OBJECT.objectApiName, fields };

        createRecord(recordInput)
            .then((contact) => {
                this.isLoading = false;
                this.dispatchEvent(
                    new ShowToastEvent({
                        title: 'Success',
                        message: `Student application submitted successfully! Record ID: ${contact.id}`,
                        variant: 'success'
                    })
                );
                this.resetForm();
            })
            .catch((error) => {
                this.isLoading = false;
                let errorMessage = 'An error occurred while submitting the application.';
                if (error && error.body && error.body.message) {
                    errorMessage = error.body.message;
                }
                this.dispatchEvent(
                    new ShowToastEvent({
                        title: 'Error Submitting Application',
                        message: errorMessage,
                        variant: 'error'
                    })
                );
            });
    }

    validateForm() {
        const allValid = [
            ...this.template.querySelectorAll('lightning-input')
        ].reduce((validSoFar, inputCmp) => {
            inputCmp.reportValidity();
            return validSoFar && inputCmp.checkValidity();
        }, true);
        return allValid;
    }

    resetForm() {
        this.firstName = '';
        this.lastName = '';
        this.email = '';
        this.phone = '';
        this.title = 'Student Applicant';
        
        const inputs = this.template.querySelectorAll('lightning-input');
        if (inputs) {
            inputs.forEach((input) => {
                input.value = '';
            });
        }
    }
}