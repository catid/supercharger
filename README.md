# supercharger

Quick demo of using an open-source AI to recursively improve its own output.  Script is designed to run on a machine with two 3090 or 4090 GPUs using model parallelism since it is based on Vicuna-13B.

## Setup

Install FastChat and the `vicuna-13b` model as described in the README here: https://github.com/lm-sys/FastChat

```bash
conda create -n fastchat python=3.10
conda activate fastchat
pip3 install fschat
pip3 install git+https://github.com/huggingface/transformers

python supercharger.py
```

## Example output

```bash
(fastchat) ➜  supercharger python supercharger.py
Loading model /home/catid/vicuna-13b
Loading checkpoint shards: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [00:09<00:00,  3.15s/it]
Loaded model with context length 2048


User prompt: What is the best way to make money with a 100W laser cutter?



Initial response:  There are several ways to make money with a 100W laser cutter, depending on your skills, interests, and resources. Here are a few options to consider:
1. Custom manufacturing: You can offer custom manufacturing services for a variety of materials, such as wood, plastic, and metal, for clients who require precise, high-quality parts and prototypes.
2. Product design and development: You can offer product design and development services, using the laser cutter to create prototypes and samples for clients.
3. Online sales: You can sell products that you create using the laser cutter on online marketplaces or through your own website.
4. Teaching and training: You can offer laser cutting workshops and training sessions to help others learn how to use the technology.
5. Collaborations: You can collaborate with other businesses or individuals on projects that require laser cutting services, such as architectural models, art installations, or custom furniture.
It's important to note that running a successful business with a laser cutter will require a combination of technical expertise, business skills, and marketing know-how. You should also consider the costs of maintaining and operating the laser cutter, as well as any necessary insurance and permits.

Asking for improvements...




Incorporating 4 suggestions:
* Grammar and spelling: The response is generally well-written, but there are a few minor errors. For example, "there are several ways to make money with a 100W laser cutter, depending on your skills, interests, and resources" could be improved to "There are several ways to make money with a 100W laser cutter, depending on your skills, interests, and resources." (score 0.9)
* Clarity and brevity: The response is clear and concise, but it could be improved by breaking up the bullet points into shorter, more focused sentences. For example, "Custom manufacturing: You can offer custom manufacturing services for a variety of materials, such as wood, plastic, and metal, for clients who require precise, high-quality parts and prototypes." could be improved to "Custom manufacturing: Offer custom manufacturing services for various materials, such as wood, plastic, and metal, to clients who require precise, high-quality parts and prototypes." (score 0.8)
* Content: The response provides a good overview of potential ways to make money with a laser cutter, but it could be improved by providing more specific information and examples. For example, "You can offer custom manufacturing services for a variety of materials, such as wood, plastic, and metal, for clients who require precise, high-quality parts and prototypes." could be expanded to include examples of the types of products that could be manufactured, such as furniture, jewelry, or electronics. (score 0.7)
* Context: The response is relevant to the prompt, but it could be improved by providing more background information and context. For example, "You can offer custom manufacturing services for a variety of materials, such as wood, plastic, and metal, for clients who require precise, high-quality parts and prototypes." could be expanded to explain what a laser cutter is and how it works, or to provide more information about the types of materials that can be cut. (score 0.6)




Incorporated feedback:  Sure, I can do that. Here is a revised response incorporating your feedback:

"There are several ways to make money with a 100W laser cutter, depending on your skills, interests, and resources. Some options to consider include:

* Custom manufacturing: If you have experience with design and engineering, you can offer custom manufacturing services for a variety of materials, such as wood, plastic, and metal. Clients who require precise, high-quality parts and prototypes will be willing to pay a premium for your services.
* Product design and development: If you have a knack for product design, you can offer product design and development services using the laser cutter to create prototypes and samples for clients. This can be a great way to showcase your skills and generate interest in your services.
* Online sales: If you enjoy creating unique and creative products, you can sell them online on platforms like Etsy or eBay. You can use the laser cutter to create a wide range of products, such as jewelry, home decor, and fashion accessories.
* Teaching and training: If you enjoy sharing your knowledge and skills with others, you can offer laser cutting workshops and training sessions to help others learn how to use the technology. This can be a great way to build a following and generate interest in your services.
* Collaborations: If you enjoy working with others, you can collaborate with other businesses or individuals on projects that require laser cutting services. For example, you could work with architects, engineers, or artists to create custom designs and prototypes.

Remember to consider the costs of maintaining and operating the laser cutter, as well as any necessary insurance and permits. It's also important to have a solid business plan and to market your services effectively in order to generate interest and generate income."

I hope this revised response is more clear, concise, and focused, and provides the information you were looking for. Please let me know if you have any further feedback or suggestions.

Checking that the feedback is an improvement...


AI decided its own feedback was an improvement score=0.9
Asking for improvements...



Done: No improvements suggested
```


So its best try is:

```
There are several ways to make money with a 100W laser cutter, depending on your skills, interests, and resources. Some options to consider include:

* Custom manufacturing: If you have experience with design and engineering, you can offer custom manufacturing services for a variety of materials, such as wood, plastic, and metal. Clients who require precise, high-quality parts and prototypes will be willing to pay a premium for your services.
* Product design and development: If you have a knack for product design, you can offer product design and development services using the laser cutter to create prototypes and samples for clients. This can be a great way to showcase your skills and generate interest in your services.
* Online sales: If you enjoy creating unique and creative products, you can sell them online on platforms like Etsy or eBay. You can use the laser cutter to create a wide range of products, such as jewelry, home decor, and fashion accessories.
* Teaching and training: If you enjoy sharing your knowledge and skills with others, you can offer laser cutting workshops and training sessions to help others learn how to use the technology. This can be a great way to build a following and generate interest in your services.
* Collaborations: If you enjoy working with others, you can collaborate with other businesses or individuals on projects that require laser cutting services. For example, you could work with architects, engineers, or artists to create custom designs and prototypes.

Remember to consider the costs of maintaining and operating the laser cutter, as well as any necessary insurance and permits. It's also important to have a solid business plan and to market your services effectively in order to generate interest and generate income.
```


Here's ChatGPT4's response:

```
A 100W laser cutter can be a versatile tool for creating various products and offering services that can help you make money. Here are some ideas to consider:

Custom engraving: Offer custom engraving services on a variety of materials such as wood, acrylic, glass, leather, and metal. You can target both individuals and businesses, creating personalized gifts, promotional items, or customized products.

Home decor and furniture: Design and manufacture unique home decor items, such as wall art, clocks, lamps, and coasters. Additionally, you can create flat-pack furniture or shelving units that can be easily assembled by the end user.

Jewelry and accessories: Use the laser cutter to create intricate jewelry designs, keychains, and other accessories from materials like wood, acrylic, and leather.

Signage and displays: Produce custom signs, plaques, and displays for businesses, events, or personal use.

Art and craft supplies: Create stencils, templates, and stamps for artists and crafters to use in their projects.

Educational kits and toys: Design and produce educational kits, puzzles, and toys that can be sold online or in local stores.

Workshops and classes: Offer workshops and classes on using a laser cutter for beginners or enthusiasts who want to learn the craft. Charge a fee for each session and provide materials for attendees to work with.

Prototyping and small-scale production: Offer prototyping and small-scale production services for inventors, designers, or small businesses that need help bringing their ideas to life.

Partner with local businesses: Collaborate with local businesses or artisans to create unique products that complement their offerings. This can help you tap into an existing customer base.

Online sales: Set up an online store to sell your products directly to customers. Use social media and online marketplaces like Etsy, eBay, or Amazon Handmade to reach a wider audience.

Remember to take into account the costs of materials, labor, and marketing when determining prices for your products or services. Additionally, ensure that you follow local regulations and safety guidelines when operating a laser cutter.
```


Which do you like better?  I personally think GPT-4 is being a lot more creative here.
