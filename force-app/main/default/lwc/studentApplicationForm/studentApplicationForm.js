import { LightningElement, track } from 'lwc';
import submitApplication from '@salesforce/apex/StudentApplicationController.submitApplication';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

export default class StudentApplicationForm extends LightningElement {
    @track firstName = '';
    @track lastName = '';
    @track email = '';
    @track phone = '';
    @track program = 'Computer Science';
    @track isSubmitting = false;

    handleInputChange(event) {
        const field = event.target.dataset.id || event.target.name;
        if (field === 'firstName') this.firstName = event.target.value;
        if (field === 'lastName') this.lastName = event.target.value;
        if (field === 'email') this.email = event.target.value;
        if (field === 'phone') this.phone = event.target.value;
        if (field === 'program') this.program = event.target.value;
    }

    async handleSubmit() {
        if (!this.lastName || !this.email) {
            this.dispatchEvent(new ShowToastEvent({
                title: 'Error',
                message: 'Please fill in required fields (Last Name & Email)',
                variant: 'error'
            }));
            return;
        }

        this.isSubmitting = true;
        const appWrapper = {
            firstName: this.firstName,
            lastName: this.lastName,
            email: this.email,
            phone: this.phone,
            program: this.program
        };

        try {
            const resultId = await submitApplication({ appData: appWrapper });
            this.dispatchEvent(new ShowToastEvent({
                title: 'Success!',
                message: `Application submitted successfully! Lead ID: ${resultId}`,
                variant: 'success'
            }));
        } catch (error) {
            this.dispatchEvent(new ShowToastEvent({
                title: 'Submission Failed',
                message: error.body ? error.body.message : error.message,
                variant: 'error'
            }));
        } finally {
            this.isSubmitting = false;
        }
    }
}